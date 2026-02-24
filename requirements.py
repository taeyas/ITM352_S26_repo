
Conversation opened. 1 unread message.

Skip to content
Using University of Hawaii Mail with screen readers

1 of 5,822
ITM-352-001: Third try
Inbox

Rick Kazman <email@mail.lamaku.hawaii.edu>
Attachments
12:18 PM (0 minutes ago)
to

Rename this file.

 One attachment
  •  Scanned by Gmail
# Assign students to specific requirements based on their student ID.

def generate_numbers(a_student_id, num_reqs):
   # Remove any dashes or spaces from the student_id
   id = ''.join(filter(str.isdigit, a_student_id))
  
   # Ensure the student_id is valid (8 digits)
   if len(id) != 8:
       raise ValueError("Invalid student ID. It should be 8 digits.")

   # Use a simple algorithm to generate two unique numbers from 1 to num_reqs
   sum_digits = sum(int(digit) for digit in id)
   first_num = (sum_digits % num_reqs) + 1

   product_digits = 1
   for digit in id:
       if int(digit) != 0:  # Avoid multiplying by zero
           product_digits *= int(digit)
   second_num = (product_digits % num_reqs) + 1

   # Ensure the numbers are different
   while second_num == first_num:
       second_num = (second_num % num_reqs) + 1

   return first_num, second_num

# Example usage
try:
   print("Welcome to the Requirements Generator!")
   student_id = input("Enter your student id (XXX-XX-XXX): ")
   num1, num2 = generate_numbers(student_id, 10)
   print(f"Your two requirements are: {num1} and {num2}")
except ValueError as e:
   print(f"Error: {e}")
requirements.txt
Displaying requirements.txt.
