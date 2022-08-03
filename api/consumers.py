import json
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import tensorflow as tf
import io
import base64

model = tf.keras.models.load_model('/Users/akshay/Desktop/Django/Backend/api/models/fer_model.h5')
pkl_filename = './models/pickle_model_logreg.pkl'



class VideoConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()
        print('text_data')
        # self.send(text_data=json.dumps({
        #     "type": "connection_established",
        #     'message': "You are connected"
        # }))

     def receive(self, text_data):
        queue = []
        queue_size = 15
        while True:
            data =  text_data
            data = data.split("$$$$")
            try:
                x, y, w, h = [int(x) for x in data[1].split(',')]
            except:
                continue
            data = data[0]
            b = io.BytesIO(base64.b64decode(data))
            pimg = Image.open(b)

            # converting RGB to BGR, as opencv standards
            frame = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGBA2GRAY)

            roi_gray = frame[y:y + w, x:x + h]
            roi_gray = cv2.resize(roi_gray, (48, 48))

            img_pixels = tf.keras.utils.img_to_array(roi_gray)
            img_pixels = np.expand_dims(img_pixels, axis=0)
            img_pixels /= 255.0

            predictions = model.predict(img_pixels)
            max_index = int(np.argmax(predictions))

            emotions = ['anger', 'happy', 'sad', 'neutral']
            predicted_emotion = emotions[max_index]

            if len(queue) == queue_size:
              queue.pop(0)
            queue.append(predicted_emotion)

            max_emotion = Counter(queue).most_common(1)[0][0]

            print(max_emotion)

            self.send(text_data=f"{max_emotion}")


