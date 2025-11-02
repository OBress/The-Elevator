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
            self.direction = 0
            self._activeTarget = self._nextTarget()
    
    def _nextTarget(self):
        """returns the next target floor"""

        # elevator is currently moving up
        if self.direction > 0:
            target = self._popUp()
            # if there is a next floor up return it
            if target is not None:
                return target
            # if there is no next floor up, elevator should move to down target
            return self._popDown()


        # elevator is currently moving down
        if self.direction < 0:
            target = self._popDown()
            # if there is a next floor down return it
            if target is not None:
                return target
            # if there is no next floor down, elevator should move to up target
            return self._popUp()


        # if elevator is idle find the closest request.
        upNext = self._peekUp()
        downNext = self._peekDown()

        # if there are no requests
        if upNext is None and downNext is None:
            return None
        # if only down request
        if upNext is None:
            return self._popDown()
        # if only up request
        if downNext is None:
            return self._popUp()

        # if there are both requests, find the closest request
        distanceUp = abs(upNext - self.currentFloor)
        distanceDown = abs(downNext - self.currentFloor)
        
        # if the up request is closer, move to the up request
        if distanceUp <= distanceDown:
            return self._popUp()
        # if the down request is closer, move to the down request
        return self._popDown()


    def _addUp(self, floor):
        """adds a floor to the up queue"""
        # avoid duplicates
        if floor in self._upSet:
            return

        heapq.heappush(self._upHeap, floor)
        self._upSet.add(floor)

    def _addDown(self, floor: int):
        """adds a floor to the down queue"""
        # avoid duplicates
        if floor in self._downSet:
            return

        # add the (-1 * floor) to the down queue so the highest floor number is the most prioritary (most negative number)
        heapq.heappush(self._downHeap, -1 * floor)
        self._downSet.add(floor)

    def _peekUp(self):
        """returns the next floor in the up queue"""
        if self._upHeap: 
            return self._upHeap[0]

        # no floors in the up queue
        return None

    def _peekDown(self):
        """returns the next floor in the down queue"""
        if self._downHeap:
            # return -1 * floor to get the highest floor number
            return -1 * self._downHeap[0]

        # no floors in the down queue
        return None

    def _popUp(self):
        """removes and returns the next floor in the up queue"""
        if self._upHeap:
            floor = heapq.heappop(self._upHeap)
            self._upSet.remove(floor)
            return floor

        # no floors in the up queue
        return None

    def _popDown(self):
        """removes and returns the next floor in the down queue"""
        if self._downHeap:
            # remove the (-1 * floor) to get the highest floor number
            floor = -1 * heapq.heappop(self._downHeap)
            self._downSet.remove(floor)
            return floor

        # no floors in the down queue
        return None

    def _validateFloor(self, floor: int):
        """validates the floor number"""
        if floor < 0:
            raise ValueError("floor cannot be negative")
        if floor > self.maxFloor:
            raise ValueError("floor cannot exceed max floor")