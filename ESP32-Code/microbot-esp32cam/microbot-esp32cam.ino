/* 
 * Proyecto MicroBot usando ESP32 CAM
 *  
 * Este código crea un servidor HTTP
 * para enviar y recibir comandos, a demás captura fotos.
 * Controla el movimiento del robot usando un driver.
 * 
 * Creado por Gerald Valverde Mc kenzie, 2023
 * Información de contacto: geraldvm167@gmail.com | gvmckenzie@mckode.com
 * 
 * Para más información sobre las conexiones eléctricas
 * y los componentes de hardware, por favor visite nuestra
 * wiki en: https://github.com/geraldvm/MicroBot/wiki
 * 
 * Copyright (c) 2023 Gerald Valverde Mc kenzie | McKode.
 *
 * Licenciado bajo la Licencia Apache, Versión 2.0 (la "Licencia");
 * no puedes usar este archivo excepto en cumplimiento con la Licencia.
 * Puedes obtener una copia de la Licencia en
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * A menos que lo requiera la ley aplicable o se acuerde por escrito, el software
 * distribuido bajo la Licencia se distribuye "tal cual",
 * SIN GARANTÍAS O CONDICIONES DE NINGÚN TIPO, ya sea expresa o implícita.
 * Consulte la Licencia para el idioma específico que rige los permisos y
 * limitaciones en virtud de la Licencia.
 *
 */


#include "credenciales.h"
#include "WiFi.h"
#include "esp_camera.h"
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"
#include "soc/soc.h"           // Disable brownour problems
#include "soc/rtc_cntl_reg.h"  // Disable brownour problems
#include "driver/rtc_io.h"
#include <ESPAsyncWebServer.h>
#include <StringArray.h>
#include <SPIFFS.h>
#include <FS.h>

// Motor Izquierdo
int MotorIzquierdaPin1 = GPIO_NUM_12; //Direccion
int MotorIzquierdaPin2 = GPIO_NUM_13; //Direccion

//Motor derecho
int MotoDerechaPin1 = GPIO_NUM_14; //Direccion
int MotoDerechaPin2 = GPIO_NUM_15; //Direccion
int flash_led = GPIO_NUM_4;

// Replace with your network credentials
const char* ssid = SECRET_SSID;
const char* password = SECRET_PASS;

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);

boolean takeNewPhoto = false;

// Photo File Name to save in SPIFFS
#define FILE_PHOTO "/photo.jpg"

// OV2640 camera module pins (CAMERA_MODEL_AI_THINKER)
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { text-align:center; }
    .vert { margin-bottom: 10%; }
    .hori{ margin-bottom: 0%; }
  </style>
</head>
<body>
  <div id="container">
    <h2>ESP32-CAM Last Photo</h2>
    <p>It might take more than 5 seconds to capture a photo.</p>
    <p>
      <button onclick="rotatePhoto();">ROTATE</button>
      <button onclick="capturePhoto()">CAPTURE PHOTO</button>
      <button onclick="location.reload();">REFRESH PAGE</button>
    </p>
  </div>
  <div><img src="saved-photo" id="photo" width="70%"></div>
</body>
<script>
  var deg = 0;
  function capturePhoto() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', "/capture", true);
    xhr.send();
  }
  function rotatePhoto() {
    var img = document.getElementById("photo");
    deg += 90;
    if(isOdd(deg/90)){ document.getElementById("container").className = "vert"; }
    else{ document.getElementById("container").className = "hori"; }
    img.style.transform = "rotate(" + deg + "deg)";
  }
  function isOdd(n) { return Math.abs(n % 2) == 1; }
</script>
</html>)rawliteral";



void setup() {
  // Serial port for debugging purposes
  Serial.begin(115200);
  
  pinMode(flash_led, OUTPUT);
  pinMode(MotorIzquierdaPin1, OUTPUT);
  pinMode(MotorIzquierdaPin2, OUTPUT);
  pinMode(MotoDerechaPin1, OUTPUT);
  pinMode(MotoDerechaPin2, OUTPUT);

  digitalWrite(flash_led, LOW);
  digitalWrite(MotorIzquierdaPin1, LOW);
  digitalWrite(MotorIzquierdaPin2, LOW);
  digitalWrite(MotoDerechaPin1, LOW);
  digitalWrite(MotoDerechaPin2, LOW);
  
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  if (!SPIFFS.begin(true)) {
    Serial.println("An Error has occurred while mounting SPIFFS");
    ESP.restart();
  }
  else {
    delay(500);
    Serial.println("SPIFFS mounted successfully");
  }

  // Print ESP32 Local IP Address
  Serial.print("IP Address: http://");
  Serial.println(WiFi.localIP());

  // Turn-off the 'brownout detector'
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  // OV2640 camera module
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }
  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    ESP.restart();
  }

  // Route for root / web page
  server.on("/", HTTP_GET, [](AsyncWebServerRequest * request) {
    request->send_P(200, "text/html", index_html);
  });

  server.on("/capture", HTTP_GET, [](AsyncWebServerRequest * request) {
    takeNewPhoto = true;
    request->send_P(200, "text/plain", "Taking Photo");
  });

  server.on("/move_forward", HTTP_GET, [](AsyncWebServerRequest * request) {
    avanzar(1);
    request->send_P(200, "text/plain", "Moviendo hacia delante");
  });

  server.on("/move_backward", HTTP_GET, [](AsyncWebServerRequest * request) {
    avanzar(0);
    request->send_P(200, "text/plain", "Moviendo hacia atrás");
  });

  server.on("/move_left", HTTP_GET, [](AsyncWebServerRequest * request) {
    girar(1);
    
    request->send_P(200, "text/plain", "Moviendo hacia la izquierda");
  });

  server.on("/move_right", HTTP_GET, [](AsyncWebServerRequest * request) {
      girar(0);
      request->send_P(200, "text/plain", "Moviendo hacia la derecha");
    });

  server.on("/stop", HTTP_GET, [](AsyncWebServerRequest * request) {
    stop();
    request->send_P(200, "text/plain", "Deteniendose");
  });

  server.on("/led", HTTP_GET, [](AsyncWebServerRequest * request) {
    digitalWrite(flash_led, HIGH);
    delay(500);
    digitalWrite(flash_led, LOW);
    delay(500);
    digitalWrite(flash_led, HIGH);
    delay(500);
    digitalWrite(flash_led, LOW);
    delay(500);
    request->send_P(200, "text/plain", "Led ON");
  });
  

  server.on("/saved-photo", HTTP_GET, [](AsyncWebServerRequest * request) {
    request->send(SPIFFS, FILE_PHOTO, "image/jpg", false);
  });
  server.on("/picture", HTTP_GET, [](AsyncWebServerRequest * request) {
    camera_fb_t * frame = NULL;
    frame = esp_camera_fb_get();
 
    request->send(SPIFFS, FILE_PHOTO, "image/jpg", false);
 
    esp_camera_fb_return(frame);
  });
  // Start server
  server.begin();

}

void loop() {
  if (takeNewPhoto) {
    capturePhotoSaveSpiffs();
    takeNewPhoto = false;
  }
  delay(1);
}

// Check if photo capture was successful
bool checkPhoto( fs::FS &fs ) {
  File f_pic = fs.open( FILE_PHOTO );
  unsigned int pic_sz = f_pic.size();
  return ( pic_sz > 100 );
}


void girar(int direccion)
{
  if(direccion == 1){
    digitalWrite(MotorIzquierdaPin1, HIGH);
    digitalWrite(MotorIzquierdaPin2, LOW);
    digitalWrite(MotoDerechaPin1, LOW);
    digitalWrite(MotoDerechaPin2, LOW);
    delay(500);
  }else if(direccion == 0){
    digitalWrite(MotorIzquierdaPin1, LOW);
    digitalWrite(MotorIzquierdaPin2, LOW);
    digitalWrite(MotoDerechaPin1, HIGH);
    digitalWrite(MotoDerechaPin2, LOW);
    delay(500);
  }stop();
}

void avanzar(int direccion)
{
  if(direccion == 1){
    digitalWrite(MotorIzquierdaPin1, HIGH);
    digitalWrite(MotorIzquierdaPin2, LOW);
    digitalWrite(MotoDerechaPin1, HIGH);
    digitalWrite(MotoDerechaPin2, LOW);
    delay(500);
  }else if(direccion == 0){
    digitalWrite(MotorIzquierdaPin1, LOW);
    digitalWrite(MotorIzquierdaPin2, HIGH);
    digitalWrite(MotoDerechaPin1, LOW);
    digitalWrite(MotoDerechaPin2, HIGH);
    delay(500);
  }
  stop();
}

void stop(){
    digitalWrite(MotorIzquierdaPin1, LOW);
    digitalWrite(MotorIzquierdaPin2, LOW);
    digitalWrite(MotoDerechaPin1, LOW);
    digitalWrite(MotoDerechaPin2, LOW);
    delay(500);
}

// Capture Photo and Save it to SPIFFS
void capturePhotoSaveSpiffs( void ) {
  camera_fb_t * fb = NULL; // pointer
  bool ok = 0; // Boolean indicating if the picture has been taken correctly

  do {
    // Take a photo with the camera
    Serial.println("Taking a photo...");

    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }

    // Photo file name
    Serial.printf("Picture file name: %s\n", FILE_PHOTO);
    File file = SPIFFS.open(FILE_PHOTO, FILE_WRITE);

    // Insert the data in the photo file
    if (!file) {
      Serial.println("Failed to open file in writing mode");
    }
    else {
      file.write(fb->buf, fb->len); // payload (image), payload length
      Serial.print("The picture has been saved in ");
      Serial.print(FILE_PHOTO);
      Serial.print(" - Size: ");
      Serial.print(file.size());
      Serial.println(" bytes");
    }
    // Close the file
    file.close();
    esp_camera_fb_return(fb);

    // check if file has been correctly saved in SPIFFS
    ok = checkPhoto(SPIFFS);
  } while ( !ok );
}
