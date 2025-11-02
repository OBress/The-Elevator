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

        # if no more targets and more steps set direction to idle
        if self._activeTarget is None and steps > 1:
            self.direction = 0

        return self.status()

    def requestFloor(self, floor, direction):
        """register a stop request for the elevator

        
        int floor: target floor (0, maxFloor)
        int direction: direction of request (1 for up, -1 for down, 0 for internal request from passenger inside)
        """
        # validate floor and direction
        self._validateFloor(floor)
        self._validateDirection(direction)

        # passenger inside requesting floor
        if direction == 0:
            # automatically determine direction based on current floor

            # when passenger requested floor is above current floor, add to up queue
            if floor > self.currentFloor:
                self._addUp(floor)
            # when passenger requested floor is below current floor, add to down queue
            elif floor < self.currentFloor:
                self._addDown(floor)
            # if floor == currentFloor, we're already there, so ignore

        # passenger outside requesting floor to go up
        elif direction == 1:
            # if elevator is already at this floor and going up (or idle), they can board immediately
            if floor == self.currentFloor and self.direction >= 0:
                # already here and compatible direction - no need to queue
                return
            self._addUp(floor)
            
        # passenger outside requesting floor to go down
        else:
            # if elevator is already at this floor and going down (or idle), they can board immediately
            if floor == self.currentFloor and self.direction <= 0:
                # already here and compatible direction - no need to queue
                return
            self._addDown(floor)
        
        # check if we need to update the active target
        self._activeTarget = self._nextTarget()

    
    
    # ------------------------------------------------------------
    # PRIVATE METHODS
    # ------------------------------------------------------------
    def _advanceOnce(self):
        """handles logic for moving elevator one step"""
        # check for new active target
        if self._activeTarget is None:
            self.direction = 0
            return
            

        # move elevator in the direction of the active target

        # elevator below the target floor
        if self.currentFloor < self._activeTarget:
            self.direction = 1
            # remove floor from up queue
            self._removeFloor(self.currentFloor)
            self.currentFloor += 1

        # elevator above the target floor
        elif self.currentFloor > self._activeTarget:
            self.direction = -1
            # remove floor from down queue
            self._removeFloor(self.currentFloor)
            self.currentFloor -= 1
        

        # arrived at the target floor
        if self.currentFloor == self._activeTarget:
            # get next target
            self._activeTarget = self._nextTarget()

    
    def _nextTarget(self):
        """returns the next target floor"""

        # elevator is currently moving up
        if self.direction > 0:
            # Priority 1: service up queue floors above current position
            target = self._peekUp(self.currentFloor)
            if target is not None:
                return target
            
            # Priority 2: go up to service down queue floors above current position
            # (continue going up to get people who want to go down, highest first)
            target = self._peekDownAbove(self.currentFloor)
            if target is not None:
                return target
            
            # Priority 3: change direction - service down queue floors below
            target = self._peekDown(self.currentFloor)
            if target is not None:
                return target
            
            # Priority 4: change direction - service up queue floors below
            return self._peekUpBelow(self.currentFloor)


        # elevator is currently moving down
        if self.direction < 0:
            # Priority 1: service down queue floors below current position
            target = self._peekDown(self.currentFloor)
            if target is not None:
                return target
            
            # Priority 2: go down to service up queue floors below current position
            # (continue going down to get people who want to go up, lowest first)
            target = self._peekUpBelow(self.currentFloor)
            if target is not None:
                return target
            
            # Priority 3: change direction - service up queue floors above
            target = self._peekUp(self.currentFloor)
            if target is not None:
                return target
            
            # Priority 4: change direction - service down queue floors above
            return self._peekDownAbove(self.currentFloor)


        # if elevator is idle find the closest request.
        # Use _peekAny methods to consider ALL floors in both queues,
        # not just floors in the "proper" direction from current position
        upNext = self._peekAnyUp()
        downNext = self._peekAnyDown()

        # if there are no valid requests
        if upNext is None and downNext is None:
            return None
        # if only down request
        if upNext is None:
            return downNext
        # if only up request
        if downNext is None:
            return upNext


        # if there are both requests, find the closest request
        distanceUp = abs(upNext - self.currentFloor)
        distanceDown = abs(downNext - self.currentFloor)

        # if the up request is closer, move to the up request
        if distanceUp <= distanceDown:
            return upNext
        # if the down request is closer, move to the down request
        return downNext



    # ------------------------------------------------------------
    # QUEUE METHODS
    # ------------------------------------------------------------
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
            # convert the negative floor to a positive floor
            floor = -1 * negFloor
            if floor < currentFloor:
                return floor
        return None
    
    def _peekAnyUp(self):
        """returns the lowest floor in the up queue (regardless of current position)"""
        if not self._upHeap:
            return None
        return min(self._upHeap)
    
    def _peekAnyDown(self):
        """returns the highest floor in the down queue (regardless of current position)"""
        if not self._downHeap:
            return None
        # remember down heap stores negative values, so min negative = highest floor
        return -1 * min(self._downHeap)
    
    def _peekDownAbove(self, currentFloor):
        """returns the highest floor in the down queue that is above currentFloor"""
        # When going up to service down requests, we want the highest floor first
        validFloors = []
        for negFloor in self._downHeap:
            floor = -1 * negFloor
            if floor > currentFloor:
                validFloors.append(floor)
        if not validFloors:
            return None
        return max(validFloors)
    
    def _peekUpBelow(self, currentFloor):
        """returns the lowest floor in the up queue that is below currentFloor"""
        # When going down to service up requests, we want the lowest floor first
        validFloors = []
        for floor in self._upHeap:
            if floor < currentFloor:
                validFloors.append(floor)
        if not validFloors:
            return None
        return min(validFloors)
    
    def _removeFloor(self, floor):
        """remove a floor from the queue based on current direction"""
        # only remove from the queue that matches our current direction
        if self.direction > 0:
            # going up, remove from up queue
            if floor in self._upSet:
                self._upSet.remove(floor)
                # rebuild the heap without this floor
                self._upHeap = [f for f in self._upHeap if f != floor]
                heapq.heapify(self._upHeap)
        
        elif self.direction < 0:
            # going down, remove from down queue
            if floor in self._downSet:
                self._downSet.remove(floor)
                # rebuild the heap without this floor (remember down heap uses negative values)
                self._downHeap = [f for f in self._downHeap if f != -floor]
                heapq.heapify(self._downHeap)

    # ------------------------------------------------------------
    # VALIDATION METHODS
    # ------------------------------------------------------------
    def _validateFloor(self, floor: int):
        """validates the floor number"""
        if floor < 0:
            raise ValueError("floor cannot be negative")
        if floor > self.maxFloor:
            raise ValueError("floor cannot exceed max floor")
    
    def _validateDirection(self, direction: int):
        """validates the direction number"""
        if direction not in (-1, 0, 1):
            raise ValueError("direction must be -1, 0, or 1")