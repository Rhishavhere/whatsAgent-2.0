import uiautomator2 as u2
from ollama import chat
import time

#constants
DEVICE_ID = 'RZCX828BLGL'
CONTACT_NAME = 'Maaaa'
MODEL_NAME = 'llama3.2:1b'

class WhatsAppAutomator:
    def __init__(self):
        self.d = u2.connect(DEVICE_ID)
        self.history = []
        self.last_processed_msg = None
        
        self._start_whatsapp()
        self._open_chat(CONTACT_NAME)

    def _start_whatsapp(self):
        self.d.app_stop('com.whatsapp')
        self.d.app_start('com.whatsapp')
        time.sleep(2)
    
    def _open_chat(self,contact_name):
        self.d(text=contact_name).click(timeout=10)
        time.sleep(2)
        self.d(text='Message').click()
        time.sleep(1)
    
    def _get_messages(self):
        messages = []
        try:
            # Get all message text elements
            message_elements = self.d(
                className='android.widget.TextView',
                resourceId='com.whatsapp:id/message_text'
            )
            
            # Get screen width once
            screen_width = self.d.info['displayWidth']
            mid_screen = screen_width / 2
            
            for element in message_elements:
                # Get element bounds
                bounds = element.info['bounds']
                x = bounds['left']
                width = bounds['right'] - bounds['left']
                
                # Calculate message center
                message_center = x + (width / 2)
                
                # Determine message type
                if message_center < mid_screen:
                    messages.append(('received', element.get_text()))
                else:
                    messages.append(('sent', element.get_text()))
                    
        except Exception as e:
            print(f"Message retrieval error: {e}")
        return messages
    
    def _get_new_messages(self):
        all_messages = self._get_messages()
        new_messages = []

        for msg_type, text in all_messages:
            if msg_type == 'received' and text != self.last_processed_msg:
                new_messages.append(text)
        
        return new_messages
    
    def _generate_response(self, prompt):
        try:
            # System prompt to guide the AI's style
            system_prompt = (
                "You are a friendly assistant chatting on WhatsApp. "
                "Respond in a casual, conversational tone. "
                "Use internet chat style: short messages, emojis."
                "Keep responses under 2 sentences. Be concise and human-like."
            )
            
            # Format chat history
            messages = [
                {'role': 'system', 'content': system_prompt},
                # *[{'role': 'user' if t == 'received' else 'assistant', 
                #   'content': c} for t, c in self.history[-6:]],
                {'role': 'user', 'content': prompt}
            ]
            
            # Generate response
            response = chat(model=MODEL_NAME, messages=messages)
            
            # Post-process response for better chat style
            return response.message.content
            
        except Exception as e:
            print(f"Generation error: {e}")
            return "Hmm, let me think about that... 🤔"
    
    def _send_message(self, text):
        try:
           
            input_field = self.d(resourceId='com.whatsapp:id/entry')
            input_field.click()
            
            
            input_field.clear_text()
            input_field.send_keys(text)
            
            
            send_button = self.d(resourceId='com.whatsapp:id/send')
            send_button.click()
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
        
    def run(self):
        print("WhatsApp Automator started...")
        while True:
            try:
                new_messages = self._get_new_messages()
                
                if new_messages:
                    latest_message = new_messages[-1]
                    print(f"New message: {latest_message}")
                    
                    
                    self.history.append(('received', latest_message))
                    
                    
                    response = self._generate_response(latest_message)
                    if response:
                        print(f"Generated response: {response}")
                        
                        
                        if self._send_message(response):
                            self.history.append(('sent', response))
                            self.last_processed_msg = latest_message
                
                time.sleep(20)  
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Main loop error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    try:
        bot = WhatsAppAutomator()
        bot.run()
    except Exception as e:
        print(f"Critical failure: {str(e)}")
        input("Press Enter to exit...")