



class Elevator:
    def __init__(self, elevatorId, maxFloor = 10, timePerFloor = 2.0):
        self.id = elevatorId
        self.maxFloor = maxFloor
        self.timePerFloor = timePerFloor

        self.currentFloor = 0
        # -1 down   0 idle   1 up
        self.direction = 0

        # maintain priority queues for up and down requests
        self._upHeap = []
        self._downHeap = []
        # maintain sets to avoid duplicate floors
        self._upSet = set()
        self._downSet = set()
        # maintain the active target floor
        self._activeTarget = None
    

    # ------------------------------------------------------------
    # PUBLIC METHODS
    # ------------------------------------------------------------
    def status(self):
        """return snapshot of the elevator state"""
        return {
            "id": self.id,
            "currentFloor": self.currentFloor,
            "direction": self.direction,
            "queueUp": sorted(self._upSet),    
            "queueDown": sorted(self._downSet, reverse=True),
            "activeTarget": self._activeTarget,
        }


    def step(self, steps = 1):
        """move elevator by the number of steps given"""
        if steps < 1:
            raise ValueError("steps must be at least 1")

        for _ in range(steps):
            self._advanceOnce()

        return self.status()
    
    
    # ------------------------------------------------------------
    # PRIVATE METHODS
    # ------------------------------------------------------------
    def _advanceOnce(self):
        """handles logic for moving elevator one step"""
        if self._activeTarget is None:
            self._activeTarget = self._nextTarget()
            
        # move elevator in the direction of the active target
        if self.currentFloor < self._activeTarget:
            self.direction = 1
            self.current_floor += 1

        elif self.currentFloor > self._activeTarget:
            self.direction = -1
            self.current_floor -= 1
        
        # arrived at the target floor
        if self.currentFloor == self._activeTarget:
            self.direction = 0
            self._activeTarget = self._nextTarget()
    
    def _nextTarget(self):
        """returns the next target floor"""
        return None

    