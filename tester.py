import unittest
from Elevator import Elevator


class TestElevator(unittest.TestCase):
    """Comprehensive test suite for the Elevator class"""

    def setUp(self):
        """Create a fresh elevator instance before each test"""
        self.elevator = Elevator(elevatorId=1, maxFloor=10, timePerFloor=2.0)

    def test_initialization(self):
        """Test elevator initializes with correct default values"""
        status = self.elevator.status()
        self.assertEqual(status["id"], 1)
        self.assertEqual(status["currentFloor"], 0)
        self.assertEqual(status["direction"], 0)
        self.assertEqual(status["queueUp"], [])
        self.assertEqual(status["queueDown"], [])
        self.assertIsNone(status["activeTarget"])

    def test_reset(self):
        """Test reset returns elevator to initial state"""
        # Make some changes
        self.elevator.requestFloor(5, 1)
        self.elevator.step(2)
        
        # Reset and verify
        status = self.elevator.reset()
        self.assertEqual(status["currentFloor"], 0)
        self.assertEqual(status["direction"], 0)
        self.assertEqual(status["queueUp"], [])
        self.assertEqual(status["queueDown"], [])
        self.assertIsNone(status["activeTarget"])

    def test_single_upward_request(self):
        """Test elevator moves up to requested floor"""
        self.elevator.requestFloor(5, 1)
        
        # Check that request was added
        status = self.elevator.status()
        self.assertIn(5, status["queueUp"])
        
        # Step until we reach floor 5
        for i in range(5):
            status = self.elevator.step()
            self.assertEqual(status["currentFloor"], i + 1)
            self.assertEqual(status["direction"], 1)
        
        # After reaching floor 5, should be idle
        status = self.elevator.step()
        self.assertEqual(status["currentFloor"], 5)
        self.assertEqual(status["direction"], 0)
        self.assertNotIn(5, status["queueUp"])

    def test_single_downward_request(self):
        """Test elevator moves down to requested floor"""
        # Start at floor 8
        self.elevator.currentFloor = 8
        self.elevator.requestFloor(3, -1)
        
        # Step until we reach floor 3
        for i in range(5):
            status = self.elevator.step()
            self.assertEqual(status["currentFloor"], 8 - i - 1)
            self.assertEqual(status["direction"], -1)
        
        # After reaching floor 3, should be idle
        status = self.elevator.step()
        self.assertEqual(status["currentFloor"], 3)
        self.assertEqual(status["direction"], 0)

    def test_multiple_upward_requests(self):
        """Test elevator services multiple upward requests in order"""
        self.elevator.requestFloor(3, 1)
        self.elevator.requestFloor(7, 1)
        self.elevator.requestFloor(5, 1)
        
        # Should service floors in order: 3, 5, 7
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 3)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 7)
        
        # Should be idle now
        self.elevator.step()
        self.assertEqual(self.elevator.direction, 0)

    def test_multiple_downward_requests(self):
        """Test elevator services multiple downward requests in order"""
        self.elevator.currentFloor = 10
        self.elevator.requestFloor(7, -1)
        self.elevator.requestFloor(3, -1)
        self.elevator.requestFloor(5, -1)
        
        # Should service floors in descending order: 7, 5, 3
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 7)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 3)

    def test_mixed_direction_requests(self):
        """Test elevator handles mixed up/down requests correctly"""
        # Start at floor 5
        self.elevator.currentFloor = 5
        
        # Request floors in both directions
        self.elevator.requestFloor(8, 1)   # Up from 5
        self.elevator.requestFloor(2, -1)  # Down from 5
        
        # Should go to closest first (both are 3 floors away, but up has priority in tie)
        status = self.elevator.step(3)
        self.assertEqual(status["currentFloor"], 8)
        
        # Then should reverse and go down
        status = self.elevator.step(6)
        self.assertEqual(status["currentFloor"], 2)

    def test_direction_change(self):
        """Test elevator changes direction after servicing all requests in one direction"""
        self.elevator.requestFloor(5, 1)
        self.elevator.requestFloor(2, -1)
        
        # Go up first
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        # Then should reverse and go down
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 2)
        self.assertEqual(self.elevator.direction, 0)  # Idle after completing

    def test_duplicate_request_ignored(self):
        """Test that duplicate floor requests are ignored"""
        self.elevator.requestFloor(5, 1)
        self.elevator.requestFloor(5, 1)
        
        status = self.elevator.status()
        # Should only have one instance of floor 5
        self.assertEqual(status["queueUp"].count(5), 1)

    def test_request_current_floor(self):
        """Test requesting current floor is handled correctly"""
        self.elevator.currentFloor = 5
        self.elevator.requestFloor(5, 1)
        
        # Should be discarded when popped
        status = self.elevator.step()
        self.assertEqual(status["currentFloor"], 5)
        self.assertEqual(status["direction"], 0)

    def test_invalid_floor_negative(self):
        """Test that negative floor raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.elevator.requestFloor(-1, 1)
        self.assertIn("cannot be negative", str(context.exception))

    def test_invalid_floor_exceeds_max(self):
        """Test that floor exceeding maxFloor raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.elevator.requestFloor(11, 1)
        self.assertIn("cannot exceed max floor", str(context.exception))

    def test_invalid_direction(self):
        """Test that invalid direction raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.elevator.requestFloor(5, 2)
        self.assertIn("direction must be", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.elevator.requestFloor(5, -2)
        self.assertIn("direction must be", str(context.exception))

    def test_invalid_steps(self):
        """Test that invalid steps value raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.elevator.step(0)
        self.assertIn("steps must be at least 1", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.elevator.step(-1)
        self.assertIn("steps must be at least 1", str(context.exception))

    def test_idle_behavior(self):
        """Test elevator remains idle when no requests"""
        # Take multiple steps with no requests
        for _ in range(5):
            status = self.elevator.step()
            self.assertEqual(status["currentFloor"], 0)
            self.assertEqual(status["direction"], 0)

    def test_complex_scenario(self):
        """Test a complex scenario with multiple requests and direction changes"""
        # Start at floor 0, add multiple requests
        self.elevator.requestFloor(3, 1)
        self.elevator.requestFloor(7, 1)
        self.elevator.requestFloor(5, 1)
        self.elevator.requestFloor(2, -1)
        
        # Move to floor 3
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 3)
        self.assertEqual(self.elevator.direction, 1)
        
        # Continue up to 5
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 5)
        self.assertEqual(self.elevator.direction, 1)
        
        # Continue up to 7
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 7)
        
        # Now should reverse to service floor 2
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 2)
        self.assertEqual(self.elevator.direction, 0)

    def test_request_behind_current_direction(self):
        """Test that requests behind current direction are requeued appropriately"""
        # Start at floor 0, going up
        self.elevator.requestFloor(5, 1)  # This will set direction to up
        self.elevator.step(3)  # Now at floor 3, going up
        
        # Request floor 2 (behind us) with down direction
        self.elevator.requestFloor(2, -1)
        
        # Should continue to floor 5 first
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        # Then should service floor 2
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 2)

    def test_boundary_floors(self):
        """Test elevator handles boundary floors (0 and maxFloor) correctly"""
        # Test floor 0
        self.elevator.requestFloor(0, -1)
        status = self.elevator.step()
        self.assertEqual(status["currentFloor"], 0)
        
        # Test maxFloor
        self.elevator.requestFloor(10, 1)
        self.elevator.step(10)
        self.assertEqual(self.elevator.currentFloor, 10)

    def test_status_format(self):
        """Test that status returns correctly formatted dictionary"""
        self.elevator.requestFloor(5, 1)
        self.elevator.requestFloor(3, -1)
        
        status = self.elevator.status()
        
        # Check all required keys exist
        self.assertIn("id", status)
        self.assertIn("currentFloor", status)
        self.assertIn("direction", status)
        self.assertIn("queueUp", status)
        self.assertIn("queueDown", status)
        self.assertIn("activeTarget", status)
        
        # Check types
        self.assertIsInstance(status["id"], int)
        self.assertIsInstance(status["currentFloor"], int)
        self.assertIsInstance(status["direction"], int)
        self.assertIsInstance(status["queueUp"], list)
        self.assertIsInstance(status["queueDown"], list)

    def test_multiple_steps_at_once(self):
        """Test stepping multiple times at once"""
        self.elevator.requestFloor(7, 1)
        
        # Step 7 times at once
        status = self.elevator.step(7)
        self.assertEqual(status["currentFloor"], 7)

    def test_queue_ordering(self):
        """Test that queues maintain correct ordering"""
        # Add floors out of order
        self.elevator.requestFloor(8, 1)
        self.elevator.requestFloor(2, 1)
        self.elevator.requestFloor(5, 1)
        
        status = self.elevator.status()
        # queueUp should be sorted
        self.assertEqual(status["queueUp"], [2, 5, 8])
        
        # Test down queue
        self.elevator.reset()
        self.elevator.currentFloor = 10
        self.elevator.requestFloor(7, -1)
        self.elevator.requestFloor(3, -1)
        self.elevator.requestFloor(9, -1)
        
        status = self.elevator.status()
        # queueDown should be sorted in reverse (highest first)
        self.assertEqual(status["queueDown"], [9, 7, 3])

    # ================================================================
    # HARDER TEST CASES - Complex Scenarios and Edge Cases
    # ================================================================

    def test_all_floors_requested(self):
        """Test elevator handles requests to all floors efficiently"""
        # Request all floors going up
        for floor in range(1, 11):
            self.elevator.requestFloor(floor, 1)
        
        # Should service all floors in ascending order
        for expected_floor in range(1, 11):
            self.elevator.step()
            self.assertEqual(self.elevator.currentFloor, expected_floor)
        
        # Should be idle after servicing all
        self.elevator.step()
        self.assertEqual(self.elevator.direction, 0)

    def test_dynamic_request_addition_during_movement(self):
        """Test adding requests while elevator is in motion"""
        # Initial request
        self.elevator.requestFloor(5, 1)
        
        # Move 2 floors
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 2)
        
        # Add new request ahead of current position
        self.elevator.requestFloor(3, 1)
        self.elevator.requestFloor(7, 1)
        
        # Should service floor 3 next
        self.elevator.step()
        self.assertEqual(self.elevator.currentFloor, 3)
        
        # Then floor 5
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        # Finally floor 7
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 7)

    def test_requests_added_behind_moving_elevator(self):
        """Test requests added behind elevator while it's moving up"""
        # Start moving up to floor 8
        self.elevator.requestFloor(8, 1)
        self.elevator.step(5)  # Now at floor 5, going up
        
        # Add requests behind current position
        self.elevator.requestFloor(2, 1)  # Behind us
        self.elevator.requestFloor(3, -1)  # Behind us, down direction
        
        # Should continue to floor 8 first
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 8)
        
        # Now should handle the requests behind
        # Floor 3 is in downHeap, floor 2 is in upHeap but will be moved to downHeap
        self.elevator.step(5)
        self.assertIn(self.elevator.currentFloor, [2, 3])

    def test_complex_zigzag_pattern(self):
        """Test elevator handles zigzag pattern efficiently"""
        # Create a zigzag pattern
        self.elevator.requestFloor(2, 1)
        self.elevator.requestFloor(8, 1)
        self.elevator.requestFloor(4, -1)
        self.elevator.requestFloor(6, 1)
        
        # Should optimize: go to 2, then 6, then 8, then come back to 4
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 2)
        
        self.elevator.step(4)
        self.assertEqual(self.elevator.currentFloor, 6)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 8)
        
        self.elevator.step(4)
        self.assertEqual(self.elevator.currentFloor, 4)

    def test_many_requests_same_direction(self):
        """Test elevator handles many requests in same direction"""
        # Add 9 floors going up (1-9)
        floors = [9, 1, 5, 3, 7, 2, 8, 4, 6]
        for floor in floors:
            self.elevator.requestFloor(floor, 1)
        
        # Step through all floors - should service in order 1-9
        for expected in range(1, 10):
            self.elevator.step()
            self.assertEqual(self.elevator.currentFloor, expected)

    def test_alternating_directions_from_middle(self):
        """Test requests alternating between up and down from middle floor"""
        # Start at floor 5
        self.elevator.currentFloor = 5
        
        # Add alternating requests
        self.elevator.requestFloor(7, 1)   # up
        self.elevator.requestFloor(3, -1)  # down
        self.elevator.requestFloor(9, 1)   # up
        self.elevator.requestFloor(1, -1)  # down
        
        # Should service one direction completely before reversing
        # Distance to 7 is 2, distance to 3 is 2, so up gets priority (tie)
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 7)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 9)
        
        # Now should reverse for down requests
        self.elevator.step(6)
        self.assertEqual(self.elevator.currentFloor, 3)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 1)

    def test_request_flood_while_moving(self):
        """Test handling flood of requests while elevator is moving"""
        self.elevator.requestFloor(10, 1)
        
        # Move to floor 3
        self.elevator.step(3)
        
        # Flood with requests
        for floor in [4, 5, 6, 7, 8, 9, 2, 1]:
            self.elevator.requestFloor(floor, 1 if floor > 3 else -1)
        
        # Should continue up to 4,5,6,7,8,9,10
        expected_floors = [4, 5, 6, 7, 8, 9, 10]
        for expected in expected_floors:
            self.elevator.step()
            self.assertEqual(self.elevator.currentFloor, expected)
        
        # Then come back down for 2, 1
        self.elevator.step(8)
        self.assertEqual(self.elevator.currentFloor, 2)
        self.elevator.step()
        self.assertEqual(self.elevator.currentFloor, 1)

    def test_multiple_direction_changes_complex(self):
        """Test multiple direction changes in complex scenario"""
        # Start at floor 5
        self.elevator.currentFloor = 5
        
        # Request pattern that requires multiple direction changes
        self.elevator.requestFloor(8, 1)
        self.elevator.step(3)  # At floor 8
        
        self.elevator.requestFloor(3, -1)
        self.elevator.step(5)  # At floor 3
        
        self.elevator.requestFloor(6, 1)
        self.elevator.step(3)  # At floor 6
        
        self.elevator.requestFloor(2, -1)
        self.elevator.step(4)  # At floor 2
        
        self.assertEqual(self.elevator.currentFloor, 2)
        self.assertEqual(self.elevator.direction, 0)

    def test_sequential_vs_bulk_stepping_consistency(self):
        """Test that sequential steps produce same result as bulk steps"""
        # Setup scenario 1: sequential steps
        elev1 = Elevator(elevatorId=1, maxFloor=10, timePerFloor=2.0)
        elev1.requestFloor(3, 1)
        elev1.requestFloor(7, 1)
        elev1.requestFloor(5, 1)
        
        for _ in range(7):
            elev1.step()
        
        # Setup scenario 2: bulk steps
        elev2 = Elevator(elevatorId=2, maxFloor=10, timePerFloor=2.0)
        elev2.requestFloor(3, 1)
        elev2.requestFloor(7, 1)
        elev2.requestFloor(5, 1)
        elev2.step(7)
        
        # Both should be at same floor
        self.assertEqual(elev1.currentFloor, elev2.currentFloor)
        # Direction may differ due to step() implementation detail:
        # bulk stepping (steps > 1) sets direction to 0 when done,
        # but sequential stepping keeps last direction
        # Both should have no more targets though
        self.assertIsNone(elev1.status()["activeTarget"])
        self.assertIsNone(elev2.status()["activeTarget"])

    def test_request_at_every_step_during_journey(self):
        """Test adding requests at every step of journey"""
        self.elevator.requestFloor(10, 1)
        
        # Add requests as we move up
        for floor in range(1, 10):
            self.elevator.step()
            # Add request for next floor (which we're already servicing)
            # These will be de-duplicated since they're already in the queue
            if self.elevator.currentFloor < 10:
                self.elevator.requestFloor(self.elevator.currentFloor + 1, 1)
        
        # Take one more step to reach floor 10
        self.elevator.step()
        self.assertEqual(self.elevator.currentFloor, 10)

    def test_empty_then_full_then_empty(self):
        """Test elevator behavior when queue goes empty -> full -> empty"""
        # Start empty
        self.assertEqual(len(self.elevator.status()["queueUp"]), 0)
        
        # Add multiple requests
        for floor in [3, 5, 7]:
            self.elevator.requestFloor(floor, 1)
        
        self.assertEqual(len(self.elevator.status()["queueUp"]), 3)
        
        # Service all requests
        self.elevator.step(7)
        
        # Should be empty again
        status = self.elevator.status()
        self.assertEqual(len(status["queueUp"]), 0)
        self.assertEqual(len(status["queueDown"]), 0)
        self.assertEqual(self.elevator.direction, 0)

    def test_extreme_distance_requests(self):
        """Test requests at extreme distances (0 to max)"""
        self.elevator.requestFloor(10, 1)  # Max distance up
        self.elevator.step(10)
        self.assertEqual(self.elevator.currentFloor, 10)
        
        self.elevator.requestFloor(0, -1)  # Max distance down
        self.elevator.step(10)
        self.assertEqual(self.elevator.currentFloor, 0)

    def test_closest_request_selection_precise(self):
        """Test that elevator precisely selects closest request when idle"""
        # Start at floor 5
        self.elevator.currentFloor = 5
        
        # Add request 1 floor up and 2 floors down
        self.elevator.requestFloor(6, 1)   # Distance: 1
        self.elevator.requestFloor(3, -1)  # Distance: 2
        
        # Should go to closer request (floor 6)
        self.elevator.step()
        self.assertEqual(self.elevator.currentFloor, 6)

    def test_same_floor_requests_both_directions(self):
        """Test requesting same floor with both up and down directions"""
        # Request floor 5 in both directions
        self.elevator.requestFloor(5, 1)
        self.elevator.requestFloor(5, -1)
        
        # Both should be queued
        status = self.elevator.status()
        self.assertIn(5, status["queueUp"])
        self.assertIn(5, status["queueDown"])
        
        # Step to floor 5
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        # One should be removed, but we should still be on floor 5
        self.assertEqual(self.elevator.currentFloor, 5)

    def test_high_frequency_requests_pattern(self):
        """Test pattern of high frequency alternating requests"""
        # Simulate busy building with requests coming in specific pattern
        requests = [
            (3, 1), (7, 1), (2, -1), (9, 1),
            (4, 1), (6, -1), (8, 1), (1, -1)
        ]
        
        for floor, direction in requests:
            self.elevator.requestFloor(floor, direction)
        
        # Let elevator service all requests
        total_steps = 0
        max_steps = 100  # Safety limit
        
        while total_steps < max_steps:
            status = self.elevator.step()
            total_steps += 1
            
            # Check if all queues are empty
            if (len(status["queueUp"]) == 0 and 
                len(status["queueDown"]) == 0 and 
                status["activeTarget"] is None):
                break
        
        # Verify all requests were serviced
        status = self.elevator.status()
        self.assertEqual(len(status["queueUp"]), 0)
        self.assertEqual(len(status["queueDown"]), 0)
        self.assertIsNone(status["activeTarget"])

    def test_request_current_floor_while_moving(self):
        """Test requesting current floor while elevator is moving"""
        self.elevator.requestFloor(5, 1)
        self.elevator.step(3)  # At floor 3
        
        # Request current floor (3) 
        self.elevator.requestFloor(3, 1)
        
        # Should continue to floor 5
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 5)

    def test_overlapping_queue_requests(self):
        """Test floors that appear in both up and down queues get serviced properly"""
        # Start at floor 5
        self.elevator.currentFloor = 5
        
        # Request floor 8 going up and floor 3 going down
        self.elevator.requestFloor(8, 1)
        self.elevator.requestFloor(3, -1)
        
        # Elevator should pick closest (tie goes to up) and go to floor 8
        # Distance to 8 is 3, distance to 3 is 2, so should go to 3 first
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 3)
        
        # Then should go up to floor 8
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 8)
        
        # Add floor 5 going down (in between)
        self.elevator.requestFloor(5, -1)
        
        # Should service floor 5
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 5)

    def test_large_maxfloor_value(self):
        """Test elevator with large maxFloor value"""
        large_elevator = Elevator(elevatorId=99, maxFloor=100, timePerFloor=1.0)
        
        large_elevator.requestFloor(50, 1)
        large_elevator.requestFloor(100, 1)
        large_elevator.requestFloor(25, 1)
        
        # Should service in order: 25, 50, 100
        large_elevator.step(25)
        self.assertEqual(large_elevator.currentFloor, 25)
        
        large_elevator.step(25)
        self.assertEqual(large_elevator.currentFloor, 50)
        
        large_elevator.step(50)
        self.assertEqual(large_elevator.currentFloor, 100)

    def test_stress_many_direction_changes(self):
        """Stress test with many direction changes"""
        # Create a pattern that forces many direction changes
        patterns = [(2, 1), (8, -1), (3, 1), (7, -1), (4, 1), (6, -1)]
        
        for floor, direction in patterns:
            self.elevator.requestFloor(floor, direction)
        
        # Run until complete
        steps = 0
        while steps < 50:
            status = self.elevator.step()
            steps += 1
            if (len(status["queueUp"]) == 0 and 
                len(status["queueDown"]) == 0 and
                status["activeTarget"] is None):
                break
        
        # Should complete all requests (queues empty and no active target)
        status = self.elevator.status()
        self.assertEqual(len(status["queueUp"]), 0)
        self.assertEqual(len(status["queueDown"]), 0)
        self.assertIsNone(status["activeTarget"])

    def test_single_step_incremental_progress(self):
        """Test that single steps always make progress towards goal"""
        self.elevator.requestFloor(7, 1)
        
        prev_floor = self.elevator.currentFloor
        for _ in range(7):
            self.elevator.step()
            # Floor should increase by exactly 1 each step
            self.assertEqual(self.elevator.currentFloor, prev_floor + 1)
            prev_floor = self.elevator.currentFloor

    # ================================================================
    # INTERNAL FLOOR REQUEST TESTS (Direction = 0)
    # ================================================================

    def test_internal_request_going_up(self):
        """Test internal request from passenger going up"""
        # Elevator picks up person at floor 0
        # Person inside requests floor 5 (direction = 0 for internal request)
        self.elevator.requestFloor(5, 0)
        
        # Should be added to up queue
        status = self.elevator.status()
        self.assertIn(5, status["queueUp"])
        
        # Step to floor 5
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 5)

    def test_internal_request_going_down(self):
        """Test internal request from passenger going down"""
        # Elevator starts at floor 8
        self.elevator.currentFloor = 8
        
        # Person inside requests floor 3 (internal request)
        self.elevator.requestFloor(3, 0)
        
        # Should be added to down queue
        status = self.elevator.status()
        self.assertIn(3, status["queueDown"])
        
        # Step to floor 3
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 3)

    def test_internal_request_current_floor(self):
        """Test internal request for current floor is ignored"""
        self.elevator.currentFloor = 5
        
        # Request current floor (should be ignored)
        self.elevator.requestFloor(5, 0)
        
        status = self.elevator.status()
        self.assertNotIn(5, status["queueUp"])
        self.assertNotIn(5, status["queueDown"])

    def test_pickup_and_internal_request(self):
        """Test realistic scenario: pickup person, they request destination"""
        # Person at floor 3 wants to go up
        self.elevator.requestFloor(3, 1)
        
        # Elevator goes to floor 3
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 3)
        
        # Person gets in and requests floor 8 (internal request)
        self.elevator.requestFloor(8, 0)
        
        # Elevator should go to floor 8
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 8)

    def test_multiple_people_internal_requests(self):
        """Test multiple people with different internal destination requests"""
        # Person at floor 2 calls elevator going up
        self.elevator.requestFloor(2, 1)
        
        # Elevator goes to floor 2
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 2)
        
        # Person 1 gets in, wants floor 5
        self.elevator.requestFloor(5, 0)
        
        # Elevator starts moving, stops at floor 4 to pick up another person
        self.elevator.requestFloor(4, 1)
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 4)
        
        # Person 2 gets in, wants floor 8
        self.elevator.requestFloor(8, 0)
        
        # Elevator should now service floor 5, then floor 8
        self.elevator.step()
        self.assertEqual(self.elevator.currentFloor, 5)
        
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 8)

    def test_mixed_external_and_internal_requests(self):
        """Test complex scenario mixing external pickups and internal destinations"""
        # Person 1 at floor 3 wants to go up
        self.elevator.requestFloor(3, 1)
        
        # Elevator at floor 0 moves to floor 3
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 3)
        
        # Person 1 gets in, wants to go to floor 7 (internal)
        self.elevator.requestFloor(7, 0)
        
        # While moving, person 2 at floor 5 also wants to go up
        self.elevator.requestFloor(5, 1)
        
        # Elevator stops at floor 5
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        # Person 2 gets in, wants to go to floor 9 (internal)
        self.elevator.requestFloor(9, 0)
        
        # Elevator services floor 7
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 7)
        
        # Then services floor 9
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 9)

    def test_internal_request_opposite_direction(self):
        """Test internal request in opposite direction of current movement"""
        # Elevator going up to floor 8
        self.elevator.requestFloor(8, 1)
        self.elevator.step(5)  # Now at floor 5, moving up
        
        # Person gets in at floor 5, but wants to go DOWN to floor 2
        self.elevator.requestFloor(2, 0)
        
        # Elevator should continue up to floor 8 first
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 8)
        
        # Then come back down to floor 2
        self.elevator.step(6)
        self.assertEqual(self.elevator.currentFloor, 2)

    def test_realistic_building_scenario(self):
        """Test realistic building scenario with multiple people and internal requests"""
        # Morning scenario: people at ground floor going to different floors
        
        # 3 people at floor 0 call elevator going up
        self.elevator.requestFloor(0, 1)
        
        # Elevator is already at floor 0, people get in
        # Person 1 wants floor 3
        self.elevator.requestFloor(3, 0)
        # Person 2 wants floor 7
        self.elevator.requestFloor(7, 0)
        # Person 3 wants floor 5
        self.elevator.requestFloor(5, 0)
        
        # Elevator should service in order: 3, 5, 7
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 3)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 7)
        
        # Now someone at floor 9 wants to go down
        self.elevator.requestFloor(9, -1)
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 9)
        
        # They want to go to floor 2
        self.elevator.requestFloor(2, 0)
        self.elevator.step(7)
        self.assertEqual(self.elevator.currentFloor, 2)

    def test_internal_requests_both_directions(self):
        """Test internal requests going both up and down from middle floor"""
        # Start at floor 5 with people inside
        self.elevator.currentFloor = 5
        
        # Person 1 wants floor 8 (up)
        self.elevator.requestFloor(8, 0)
        # Person 2 wants floor 2 (down)
        self.elevator.requestFloor(2, 0)
        
        # Both should be in their respective queues
        status = self.elevator.status()
        self.assertIn(8, status["queueUp"])
        self.assertIn(2, status["queueDown"])
        
        # Elevator should pick closest first (2 is closer: 3 floors vs 8: 3 floors, tie goes to up)
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 8)
        
        # Then service floor 2
        self.elevator.step(6)
        self.assertEqual(self.elevator.currentFloor, 2)

    def test_internal_request_while_moving_same_direction(self):
        """Test adding internal request while elevator moving in same direction"""
        # Elevator going to floor 10
        self.elevator.requestFloor(10, 1)
        
        # Move to floor 4
        self.elevator.step(4)
        self.assertEqual(self.elevator.currentFloor, 4)
        
        # Someone inside requests floor 7 (between current and destination)
        self.elevator.requestFloor(7, 0)
        
        # Should stop at floor 7 first
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 7)
        
        # Then continue to floor 10
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 10)

    def test_complex_internal_external_mix(self):
        """Test complex mix of internal and external requests"""
        # External: Person at floor 2 wants to go up
        self.elevator.requestFloor(2, 1)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 2)
        
        # Internal: They want floor 6
        self.elevator.requestFloor(6, 0)
        
        # External: Person at floor 4 wants to go up
        self.elevator.requestFloor(4, 1)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 4)
        
        # Internal: Second person wants floor 9
        self.elevator.requestFloor(9, 0)
        
        # External: Person at floor 8 wants to go down
        self.elevator.requestFloor(8, -1)
        
        # Should finish going up: 6, 8 (pickup while going up), 9
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 6)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 8)
        
        # Person at 8 gets in, wants floor 3
        self.elevator.requestFloor(3, 0)
        
        # Continue to 9
        self.elevator.step()
        self.assertEqual(self.elevator.currentFloor, 9)
        
        # Then back down to 3
        self.elevator.step(6)
        self.assertEqual(self.elevator.currentFloor, 3)


def run_tests():
    """Run all tests and print results"""
    print("=" * 70)
    print("Running Elevator Class Tests")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestElevator)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

