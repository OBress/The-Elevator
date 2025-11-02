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
        self._updateActiveTarget()
    
    
    # ------------------------------------------------------------
    # PRIVATE METHODS
    # ------------------------------------------------------------
    def _advanceOnce(self):
        """handles logic for moving elevator one step"""
        # check for new active target
        if self._activeTarget is None:
            self._activeTarget = self._nextTarget()
            # if there is no next target, elevator should idle (direction already set by _nextTarget)
            if self._activeTarget is None:
                return
            

        # move elevator in the direction of the active target
        # (direction is already set correctly by _nextTarget)

        # elevator below the target floor
        if self.currentFloor < self._activeTarget:
            self.currentFloor += 1

        # elevator above the target floor
        elif self.currentFloor > self._activeTarget:
            self.currentFloor -= 1
        

        # arrived at the target floor
        if self.currentFloor == self._activeTarget:
            # remove the floor from the appropriate queue now that we've reached it
            self._removeFloorFromQueue(self._activeTarget)
            # get next target (and update direction)
            self._activeTarget = self._nextTarget()
    
    def _nextTarget(self):
        """returns the next target floor and updates direction"""
        target = None
        
        # elevator is currently moving up
        if self.direction > 0:
            # only service floors above current position when going up
            target = self._peekUp(self.currentFloor)
            # if there is a next floor up return it
            if target is not None:
                self._setDirection(target)
                return target
            # if there is no next floor up, elevator should move to down target
            target = self._peekDown(self.currentFloor)


        # elevator is currently moving down
        elif self.direction < 0:
            # only service floors below current position when going down
            target = self._peekDown(self.currentFloor)
            # if there is a next floor down return it
            if target is not None:
                self._setDirection(target)
                return target
            # if there is no next floor down, elevator should move to up target
            target = self._peekUp(self.currentFloor)


        # if elevator is idle find the closest request.
        else:
            upNext = self._peekUp(self.currentFloor)
            downNext = self._peekDown(self.currentFloor)

            # if there are no valid requests in proper positions
            if upNext is None and downNext is None:
                self._setDirection(None)
                return None
            # if only down request
            if upNext is None:
                target = downNext
            # if only up request
            elif downNext is None:
                target = upNext
            # if there are both requests, find the closest request
            else:
                distanceUp = abs(upNext - self.currentFloor)
                distanceDown = abs(downNext - self.currentFloor)

                # if the up request is closer, move to the up request
                if distanceUp <= distanceDown:
                    target = upNext
                # if the down request is closer, move to the down request
                else:
                    target = downNext
        
        # update direction based on target
        self._setDirection(target)
        return target
    
    def _setDirection(self, target):
        """set direction based on target floor"""
        if target is None:
            self.direction = 0  # idle
        elif target > self.currentFloor:
            self.direction = 1  # up
        elif target < self.currentFloor:
            self.direction = -1  # down
        # if target == currentFloor, keep current direction


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

    def _updateActiveTarget(self):
        """update active target if a closer floor should be serviced first"""
        
        # if elevator is idle, check if there's a new request and set initial target
        if self.direction == 0:
            if self._activeTarget is None:
                # no active target yet, find one
                self._activeTarget = self._nextTarget()
            return
        
        # check if there is a closer floor that should be serviced first versus the active target
        if self.direction > 0:
            # check if there is a floor in the up queue between current and active target
            closerFloor = self._peekUp(self.currentFloor)
            if closerFloor is not None and closerFloor < self._activeTarget:
                # update target to the closer floor (old target stays in queue)
                self._activeTarget = closerFloor
                self._setDirection(closerFloor)
        
        elif self.direction < 0:
            # check if there is a closer floor that should be serviced first versus the active target
            closerFloor = self._peekDown(self.currentFloor)
            if closerFloor is not None and closerFloor > self._activeTarget:
                # update target to the closer floor (old target stays in queue)
                self._activeTarget = closerFloor
                self._setDirection(closerFloor)
    
    def _removeFloorFromQueue(self, floor):
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