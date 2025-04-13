class State:
    _instance = None
    _state = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(State, cls).__new__(cls)
        return cls._instance

    def update(self, new_state):
        self._state.update(new_state)

    def get(self):
        return self._state

state = State()