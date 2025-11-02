



class Elevator:
    def __init__(self, elevatorId, maxFloor = 10, timePerFloor = 2.0):
        self.id = elevatorId
        self.maxFloor = maxFloor
        self.timePerFloor = timePerFloor

        self.currentFloor = 0
        self.direction = 0  # -1 down   0 idle   1 up

        # maintain priority queues for up and down requests
        self._upHeap = []
        self._downHeap = []
        # maintain sets to avoid duplicate floors
        self._upSet = set()
        self._downSet = set()
        



    