from machine import Pin, SPI
from max7219 import Matrix8x8
import utime

class LEDMatrixManager:
    def __init__(self, spi, cs_pin1, cs_pin2, num_matrices):
        self.display1 = Matrix8x8(spi, cs_pin1, num_matrices)
        self.display2 = Matrix8x8(spi, cs_pin2, num_matrices)
        self.display1.brightness(5)
        self.display2.brightness(5)
        self.current_row = 0
        self.current_col = 0

        self.centre_points = [
            [[12, 6, 1, ' '], [8, 6, 1, ' '], [20, 6, 1, ' ']],
            [[12, 2, 2, ' '], [8, 2, 2, ' '], [20, 2, 2, ' ']],
            [[12, 6, 2, ' '], [8, 6, 2, ' '], [20, 6, 2, ' ']]
        ]

        self.current_player = 'X'

        # Set initial cursor position on startup
        x, y, display, _ = self.centre_points[self.current_row][self.current_col]
        self.set_pixel(x, y, display)

    def draw_grid(self):
        # Draw grid on both matrices
        for y in range(12):
            self.display1.pixel(10, y+4, 1)
            self.display2.pixel(10, y, 1)

        for y in range(12):
            self.display2.pixel(22, y, 1)
            self.display1.pixel(22, y+4, 1)

        for x in range(16):
            self.display2.pixel(x + 8, 4, 1)

        for x in range(16):
            self.display2.pixel(x + 8, 0, 1)

        self.display1.show()
        self.display2.show()
        print("Grid drawn on both displays")

    def set_pixel(self, x, y, display):
        if display == 1:
            self.display1.pixel(x, y, 1)
            self.display1.show()
        elif display == 2:
            self.display2.pixel(x, y, 1)
            self.display2.show()
    
    def clear_pixel(self, x, y, display):
        if display == 1:
            self.display1.pixel(x, y, 0)
            self.display1.show()
        elif display == 2:
            self.display2.pixel(x, y, 0)
            self.display2.show()

    def clear(self):
        self.display1.fill(0)
        self.display1.show()
        self.display2.fill(0)
        self.display2.show()
        print("Displays cleared")

    def is_cell_empty(self, row, col):
        return self.centre_points[row][col][3] == ' '

    def move_cursor(self, direction):
        original_row, original_col = self.current_row, self.current_col

        x, y, display, _ = self.centre_points[self.current_row][self.current_col]
        self.clear_pixel(x, y, display)
        
        while True:
            if direction == 'up':
                new_row = self.current_row - 1
                if new_row < 0:
                    new_row = len(self.centre_points) - 1  # Wrap to the bottom row

                if self.is_cell_empty(new_row, self.current_col):
                    self.current_row = new_row
                    break
                else:
                    self.current_row = new_row  # Move cursor to next cell
                
            elif direction == 'right':
                new_col = self.current_col + 1
                if new_col >= len(self.centre_points[0]):
                    new_col = 0  # Wrap to the first column

                if self.is_cell_empty(self.current_row, new_col):
                    self.current_col = new_col
                    break
                else:
                    self.current_col = new_col  # Move cursor to next cell

            # Prevent infinite loop if all cells are occupied
            if self.current_row == original_row and self.current_col == original_col:
                break

        x, y, display, _ = self.centre_points[self.current_row][self.current_col]
        self.set_pixel(x, y, display)

        return self.current_row, self.current_col  # Return updated cursor position

    def make_move(self):
        row, col = self.current_row, self.current_col
        if self.centre_points[row][col][3] == ' ':
            self.centre_points[row][col][3] = self.current_player 
            x, y, display, _ = self.centre_points[row][col]
            if self.current_player == 'X':
                self.draw_cross(display, x, y)
            else:
                self.draw_naught(display, x, y)

            if self.check_win(self.current_player):
                print(f"Player {self.current_player} wins!")
            elif self.check_draw():
                print("The game is a draw!")
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
        else:
            print("Invalid move, the cell is already occupied. Try again.")

    def check_win(self, player):
        for row in self.centre_points:
            if all(cell[3] == player for cell in row):
                return True

        for col in range(3):
            if all(self.centre_points[row][col][3] == player for row in range(3)):
                return True

        if all(self.centre_points[i][i][3] == player for i in range(3)):
            return True
        if all(self.centre_points[i][2 - i][3] == player for i in range(3)):
            return True
        return False

    def check_draw(self):
        for row in self.centre_points:
            if any(cell[3] == ' ' for cell in row):
                return False
        return True

    def draw_cross(self, display, x, y):
      last_x, last_y, last_display = x, y, display
      self.clear_pixel(x, y, display)

      for direction in ['up', 'right']:
        original_row, original_col = self.current_row, self.current_col
        self.move_cursor(direction)
        new_x, new_y, new_display, _ = self.centre_points[self.current_row][self.current_col]
        if self.is_cell_empty(self.current_row, self.current_col):
          self.set_pixel(new_x, new_y, new_display)
          break
        else:
          self.current_row, self.current_col = original_row, original_col
      if (last_x, last_y) not in [(8, 6), (8, 2)]:
        if display == 1:
          self.display1.pixel(last_x, last_y, 1)
          self.display1.pixel(last_x + 1, last_y - 1, 1)
          self.display1.pixel(last_x + 1, last_y + 1, 1)
          self.display1.pixel(last_x - 1, last_y - 1, 1)
          self.display1.pixel(last_x - 1, last_y + 1, 1)
          self.display1.show()
          print("Cross drawn on display 1")

        elif display == 2:
          self.display2.pixel(last_x, last_y, 1)
          self.display2.pixel(last_x + 1, last_y - 1, 1)
          self.display2.pixel(last_x + 1, last_y + 1, 1)
          self.display2.pixel(last_x - 1, last_y - 1, 1)
          self.display2.pixel(last_x - 1, last_y + 1, 1)
          self.display2.show()
          print("Cross drawn on display 2")
      else:
        if display == 1:
          self.display1.pixel(last_x, last_y, 1)
          self.display1.pixel(last_x + 1, last_y - 1, 1)
          self.display1.pixel(last_x + 1, last_y + 1, 1)
          self.display1.pixel(23, last_y - 1, 1)
          self.display1.pixel(23, last_y + 1, 1)
          self.display1.show()
          print("Cross drawn on display 1")

        elif display == 2:
          self.display2.pixel(last_x, last_y, 1)
          self.display2.pixel(last_x + 1, last_y - 1, 1)
          self.display2.pixel(last_x + 1, last_y + 1, 1)
          self.display2.pixel(23, last_y - 1, 1)
          self.display2.pixel(23, last_y + 1, 1)
          self.display2.show()
          print("Cross drawn on display 2")

    def draw_naught(self, display, x, y):
        last_x, last_y, last_display = x, y, display
        self.clear_pixel(x, y, display)

        for direction in ['up', 'right']:
            original_row, original_col = self.current_row, self.current_col
            self.move_cursor(direction)
            new_x, new_y, new_display, _ = self.centre_points[self.current_row][self.current_col]
            if self.is_cell_empty(self.current_row, self.current_col):
                self.set_pixel(new_x, new_y, new_display)
                break
            else:
                self.current_row, self.current_col = original_row, original_col
        if (last_x, last_y) not in [(8, 6), (8, 2)]:
          if display == 1:
            self.display1.pixel(last_x, last_y - 1, 1)
            self.display1.pixel(last_x, last_y + 1, 1)
            self.display1.pixel(last_x - 1, last_y, 1)
            self.display1.pixel(last_x + 1, last_y, 1)
            self.display1.show()
            print("Naught drawn on display 1")
          elif display == 2:
            self.display2.pixel(last_x, last_y - 1, 1)
            self.display2.pixel(last_x, last_y + 1, 1)
            self.display2.pixel(last_x - 1, last_y, 1)
            self.display2.pixel(last_x + 1, last_y, 1)
            self.display2.show()
            print("Naught drawn on display 2")
        else:
          if display == 1:
            self.display1.pixel(last_x, last_y - 1, 1)
            self.display1.pixel(last_x, last_y + 1, 1)
            self.display1.pixel(23, last_y, 1)
            self.display1.pixel(9, last_y, 1)
            self.display1.show()
            print("Naught drawn on display 1")
          elif display == 2:
            self.display2.pixel(last_x, last_y - 1, 1)
            self.display2.pixel(last_x, last_y + 1, 1)
            self.display2.pixel(23, last_y, 1)
            self.display2.pixel(9, last_y, 1)
            self.display2.show()
            print("Naught drawn on display 2")
          
    def restart_the_game(self, grid):
        #I would like to reset the grid status for #3
        pass


# Initialize SPI
spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))

# Initialize display managers
cs1 = Pin(5, Pin.OUT)
cs2 = Pin(9, Pin.OUT)
display_manager = LEDMatrixManager(spi, cs1, cs2, 4)

# Clear displays initially
display_manager.clear()

# Create grid
display_manager.draw_grid()

# Set up GPIO pins for buttons
button1 = Pin(12, Pin.IN)
button2 = Pin(13, Pin.IN)
button3 = Pin(14, Pin.IN)

# Initialize previous states for buttons
previous_state1 = button1.value()
previous_state2 = button2.value()
previous_state3 = button3.value()

# Timer variables
debounce_timeout = 200  # Debounce timeout in milliseconds
last_high_time = [0, 0, 0]  # Last time each button was detected as high (milliseconds)

while True:
    # Read current states of buttons
    current_state1 = button1.value()
    current_state2 = button2.value()
    current_state3 = button3.value()
    
    # Check if button 1 state has changed
    if current_state1 != previous_state1:
        if current_state1 == 1 and (last_high_time[0] == 0 or utime.ticks_diff(utime.ticks_ms(), last_high_time[0]) >= debounce_timeout):
            print("Button 1 pressed")
            display_manager.make_move() # Trigger to make move
            last_high_time[0] = utime.ticks_ms()
        
        previous_state1 = current_state1
    
    # Check if button 2 state has changed
    if current_state2 != previous_state2:
        if current_state2 == 1 and (last_high_time[1] == 0 or utime.ticks_diff(utime.ticks_ms(), last_high_time[1]) >= debounce_timeout):
            print("Button 2 pressed")
            display_manager.move_cursor('up')
            last_high_time[1] = utime.ticks_ms()
        
        previous_state2 = current_state2
    
    # Check if button 3 state has changed
    if current_state3 != previous_state3:
        if current_state3 == 1 and (last_high_time[2] == 0 or utime.ticks_diff(utime.ticks_ms(), last_high_time[2]) >= debounce_timeout):
            print("Button 3 pressed")
            display_manager.move_cursor('right')
            last_high_time[2] = utime.ticks_ms()
        
        previous_state3 = current_state3
