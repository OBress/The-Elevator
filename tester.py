import unittest
from Elevator import Elevator


class TestElevator(unittest.TestCase):
    """Focused test suite for the Elevator class covering edge cases and core functionality"""

    def setUp(self):
        """Create a fresh elevator instance before each test"""
        self.elevator = Elevator(elevatorId=1, maxFloor=10, timePerFloor=2.0)

    # ================================================================
    # VALIDATION & EDGE CASES
    # ================================================================

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

    def test_invalid_steps(self):
        """Test that invalid steps value raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.elevator.step(0)
        self.assertIn("steps must be at least 1", str(context.exception))

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

    def test_duplicate_request_ignored(self):
        """Test that duplicate floor requests are ignored"""
        self.elevator.requestFloor(5, 1)
        self.elevator.requestFloor(5, 1)
        
        status = self.elevator.status()
        self.assertEqual(status["queueUp"].count(5), 1)

    def test_request_current_floor(self):
        """Test requesting current floor is handled correctly"""
        self.elevator.currentFloor = 5
        self.elevator.requestFloor(5, 1)
        
        status = self.elevator.step()
        self.assertEqual(status["currentFloor"], 5)
        self.assertEqual(status["direction"], 0)

    def test_same_floor_requests_both_directions(self):
        """Test requesting same floor with both up and down directions"""
        self.elevator.requestFloor(5, 1)
        self.elevator.requestFloor(5, -1)
        
        status = self.elevator.status()
        self.assertIn(5, status["queueUp"])
        self.assertIn(5, status["queueDown"])
        
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 5)

    def test_idle_behavior(self):
        """Test elevator remains idle when no requests"""
        for _ in range(5):
            status = self.elevator.step()
            self.assertEqual(status["currentFloor"], 0)
            self.assertEqual(status["direction"], 0)

    # ================================================================
    # DIRECTION CHANGES & MIXED REQUESTS
    # ================================================================

    def test_direction_change(self):
        """Test elevator changes direction after servicing all requests in one direction"""
        self.elevator.requestFloor(5, 1)
        self.elevator.requestFloor(2, -1)
        
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 2)
        self.assertEqual(self.elevator.direction, 0)

    def test_request_behind_current_direction(self):
        """Test that requests behind current direction are requeued appropriately"""
        self.elevator.requestFloor(5, 1)
        self.elevator.step(3)  # At floor 3, going up
        
        self.elevator.requestFloor(2, -1)
        
        # Should continue to floor 5 first
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        # Then service floor 2
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 2)

    def test_alternating_directions_from_middle(self):
        """Test requests alternating between up and down from middle floor"""
        self.elevator.currentFloor = 5
        
        self.elevator.requestFloor(7, 1)
        self.elevator.requestFloor(3, -1)
        self.elevator.requestFloor(9, 1)
        self.elevator.requestFloor(1, -1)
        
        # Should service one direction completely before reversing
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 7)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 9)
        
        self.elevator.step(6)
        self.assertEqual(self.elevator.currentFloor, 3)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 1)

    def test_closest_request_selection_precise(self):
        """Test that elevator precisely selects closest request when idle"""
        self.elevator.currentFloor = 5
        
        self.elevator.requestFloor(6, 1)   # Distance: 1
        self.elevator.requestFloor(3, -1)  # Distance: 2
        
        # Should go to closer request (floor 6)
        self.elevator.step()
        self.assertEqual(self.elevator.currentFloor, 6)

    # ================================================================
    # INTERNAL REQUESTS (Direction = 0)
    # ================================================================

    def test_internal_request_going_up(self):
        """Test internal request from passenger going up"""
        self.elevator.requestFloor(5, 0)
        
        status = self.elevator.status()
        self.assertIn(5, status["queueUp"])
        
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 5)

    def test_internal_request_going_down(self):
        """Test internal request from passenger going down"""
        self.elevator.currentFloor = 8
        self.elevator.requestFloor(3, 0)
        
        status = self.elevator.status()
        self.assertIn(3, status["queueDown"])
        
        self.elevator.step(5)
        self.assertEqual(self.elevator.currentFloor, 3)

    def test_internal_request_current_floor(self):
        """Test internal request for current floor is ignored"""
        self.elevator.currentFloor = 5
        self.elevator.requestFloor(5, 0)
        
        status = self.elevator.status()
        self.assertNotIn(5, status["queueUp"])
        self.assertNotIn(5, status["queueDown"])

    def test_internal_request_opposite_direction(self):
        """Test internal request in opposite direction of current movement"""
        self.elevator.requestFloor(8, 1)
        self.elevator.step(5)  # At floor 5, moving up
        
        # Person gets in, wants to go DOWN to floor 2
        self.elevator.requestFloor(2, 0)
        
        # Should continue up to floor 8 first
        self.elevator.step(3)
        self.assertEqual(self.elevator.currentFloor, 8)
        
        # Then come back down to floor 2
        self.elevator.step(6)
        self.assertEqual(self.elevator.currentFloor, 2)

    def test_mixed_external_and_internal_requests(self):
        """Test complex scenario mixing external pickups and internal destinations"""
        self.elevator.requestFloor(3, 1)
        self.elevator.step(3)
        
        self.elevator.requestFloor(7, 0)
        self.elevator.requestFloor(5, 1)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 5)
        
        self.elevator.requestFloor(9, 0)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 7)
        
        self.elevator.step(2)
        self.assertEqual(self.elevator.currentFloor, 9)


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

