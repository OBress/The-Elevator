import heapq
from typing import Optional



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
        # active target floor
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
            "queueDown": sorted(self._downSet, reverse=True), # sorted in reverse since highest is most prioritary
            "activeTarget": self._activeTarget,
        }

    def reset(self):
        """reset the elevator to a default state"""
        self.currentFloor = 0
        self.direction = 0
        self._upSet = set()
        self._downSet = set()
        self._upHeap = []
        self._downHeap = []
        self._activeTarget = None
        return self.status()

    def step(self, steps = 1):
        """move elevator by the number of steps given"""
        if steps < 1:
            raise ValueError("steps must be at least 1")

        for _ in range(steps):
            self._advanceOnce()

        return self.status()

    def requestFloor(self, floor, direction):
        """register a stop request for the elevator

        
        int floor: target floor (0, maxFloor)
        int direction: direction of request (1 for up, -1 for down)
        """
        # validate floor and direction
        self._validateFloor(floor)
        self._validateDirection(direction)

        # add the request to the appropriate queue
        if direction == 1:
            self._addUp(floor)
        else:
            self._addDown(floor)
    
    
    # ------------------------------------------------------------
    # PRIVATE METHODS
    # ------------------------------------------------------------
    def _advanceOnce(self):
        """handles logic for moving elevator one step"""
        # check for new active target
        if self._activeTarget is None:
            self._activeTarget = self._nextTarget()
            # if there is no next target, elevator should idle
            if self._activeTarget is None:
                self.direction = 0
                return
            

        # move elevator in the direction of the active target

        # elevator below the target floor
        if self.currentFloor < self._activeTarget:
            self.direction = 1
            self.currentFloor += 1

        # elevator above the target floor
        elif self.currentFloor > self._activeTarget:
            self.direction = -1
            self.currentFloor -= 1
        

        # arrived at the target floor
        if self.currentFloor == self._activeTarget:
            # get next target before updating direction
            self._activeTarget = self._nextTarget()
            # if no next target, go idle
            if self._activeTarget is None:
                self.direction = 0
    
    def _nextTarget(self):
        """returns the next target floor"""

        # elevator is currently moving up
        if self.direction > 0:
            # only service floors above current position when going up
            target = self._popUp(self.currentFloor)
            # if there is a next floor up return it
            if target is not None:
                return target
            # if there is no next floor up, elevator should move to down target
            return self._popDown(self.currentFloor)


        # elevator is currently moving down
        if self.direction < 0:
            # only service floors below current position when going down
            target = self._popDown(self.currentFloor)
            # if there is a next floor down return it
            if target is not None:
                return target
            # if there is no next floor down, elevator should move to up target
            return self._popUp(self.currentFloor)


        # if elevator is idle find the closest request.
        upNext = self._peekUp(self.currentFloor)
        downNext = self._peekDown(self.currentFloor)

        # if there are no requests
        if upNext is None and downNext is None:
            return None
        # if only down request
        if upNext is None:
            return self._popDown(self.currentFloor)
        # if only up request
        if downNext is None:
            return self._popUp(self.currentFloor)


        # if there are both requests, find the closest request
        distanceUp = abs(upNext - self.currentFloor)
        distanceDown = abs(downNext - self.currentFloor)

        # if the up request is closer, move to the up request
        if distanceUp <= distanceDown:
            return self._popUp(self.currentFloor)
        # if the down request is closer, move to the down request
        return self._popDown(self.currentFloor)


    def _addUp(self, floor):
        """adds a floor to the up queue"""
        # avoid duplicates
        if floor in self._upSet:
            return False

        heapq.heappush(self._upHeap, floor)
        self._upSet.add(floor)
        return True

    def _addDown(self, floor: int):
        """adds a floor to the down queue"""
        # avoid duplicates
        if floor in self._downSet:
            return False

        # add the (-1 * floor) to the down queue so the highest floor number is the most prioritary (most negative number)
        heapq.heappush(self._downHeap, -1 * floor)
        self._downSet.add(floor)
        return True

    def _peekUp(self, currentFloor):
        """returns the next floor in the up queue that is above currentFloor"""
        # iterate through the heap to find the first valid floor (highest floor > currentFloor)
        for floor in sorted(self._upHeap):
            if floor > currentFloor:
                return floor
        return None

    def _peekDown(self, currentFloor):
        """returns the next floor in the down queue that is below currentFloor"""
        # iterate through the heap to find the first valid floor (highest floor < currentFloor)
        for negFloor in sorted(self._downHeap):
            floor = -1 * negFloor
            if floor < currentFloor:
                return floor
        return None

    def _popUp(self, currentFloor):
        """removes and returns the next floor in the up queue that is above currentFloor"""
        # keep popping until we find a floor above currentFloor or heap is empty
        while self._upHeap:
            floor = heapq.heappop(self._upHeap)
            self._upSet.remove(floor)
            
            if floor > currentFloor:
                # found a valid floor above current position
                return floor
            elif floor < currentFloor:
                # floor is behind us, add it to down queue
                self._addDown(floor)
            # if floor == currentFloor, we're already there, discard it
        
        # no floors in the up queue above currentFloor
        return None

    def _popDown(self, currentFloor):
        """removes and returns the next floor in the down queue that is below currentFloor"""
        # keep popping until we find a floor below currentFloor or heap is empty
        while self._downHeap:
            floor = -1 * heapq.heappop(self._downHeap)
            self._downSet.remove(floor)
            
            if floor < currentFloor:
                # found a valid floor below current position
                return floor
            elif floor > currentFloor:
                # floor is behind us, add it to up queue
                self._addUp(floor)
            # if floor == currentFloor, we're already there, discard it
        
        # no floors in the down queue below currentFloor
        return None

    def _validateFloor(self, floor: int):
        """validates the floor number"""
        if floor < 0:
            raise ValueError("floor cannot be negative")
        if floor > self.maxFloor:
            raise ValueError("floor cannot exceed max floor")
    
    def _validateDirection(self, direction: int):
        """validates the direction number"""
        if direction not in (-1, 1):
            raise ValueError("direction must be -1 or 1")