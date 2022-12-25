from transitions.extensions import GraphMachine

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
    
    def is_going_to_weather(self, event):
        text = event.message.text
        return text.lower() == "go to weather"

    def is_going_to_city(self, event):
        text = event.message.text
        return text.lower() == "go to city"

    def is_going_to_fortune(self, event):
        text = event.message.text
        return text.lower() == "go to fortune"

    def on_exit_weather(self):
        print("Leaving weather")

    def on_exit_fortune(self, event):
        print("Leaving fortune")

    def on_exit_city(self):
        print("Leaving city")
