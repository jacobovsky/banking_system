# Write your code here
import random
import sys
import sqlite3


class BankAccount:
    def __init__(self, card_id, card_pin):
        self.card_id = card_id
        self.card_pin = card_pin
        self.balance = 0

    def show_balance(self):
        print("Balance: {}".format(self.balance))


def generate_card_id():
    global list_of_accounts
    while 1:
        nine_digits = random.randint(10 ** 8, 10 ** 9 - 1)
        card_id = '400000' + str(nine_digits)
        sum_of_15_digits = 0
        counter_odd = 1
        for digit in list(card_id):
            digit = int(digit)
            if counter_odd % 2 == 1:
                digit = digit * 2
                if digit > 9:
                    digit -= 9
                else:
                    pass
            else:
                pass
            sum_of_15_digits += digit
            counter_odd += 1
        if sum_of_15_digits % 10 == 0:
            last_digit = 0
        else:
            last_digit = 10 - sum_of_15_digits % 10
        card_id = card_id + f'{last_digit}'
        # Check if it is not duplicate
        is_duplicate = False
        for account in list_of_accounts:
            if account.card_id == card_id:
                is_duplicate = True
        if not is_duplicate:
            return int(card_id)
        else:
            pass


def generate_card_pin():
    return random.randint(1000, 9999)


def is_luhn(num):
    counter = 1
    temp_arr = []
    for digit in list(num):
        if counter % 2 == 1:
            temp_arr.append(int(digit)*2)
        else:
            temp_arr.append(int(digit))
        if temp_arr[-1] > 9:
            temp_arr[-1] -= 9
        counter += 1
    if sum(temp_arr) % 10 == 0:
        return True
    else:
        return False


# creating database using SQL
connection = sqlite3.connect('card.s3db')
cursor = connection.cursor()
cursor.execute('''DROP TABLE card;''')  # delete prev table
cursor.execute('''CREATE TABLE card(
                id INTEGER, 
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0
                );''')
connection.commit()
list_of_accounts = []
while 1:
    key = int(input("1. Create an account\n"
                    "2. Log into account\n"
                    "0. Exit\n"))
    if key == 1:
        new_card_num = generate_card_id()
        new_card_pin = generate_card_pin()
        list_of_accounts.append(BankAccount(new_card_num, new_card_pin))
        print("\nYour card has been created\n\n"
              "Your card number:\n"
              "{}\n"
              "Your card PIN:\n"
              "{}\n".format(new_card_num, new_card_pin))
        # need to get rid of list_of_accounts to truly depend on sql database (I guess)
        # generate a new id based on the highest value in an id set
        cursor.execute(f'''SELECT MAX(id) FROM card;''')
        new_card_id = cursor.fetchone()[0]  # it takes value of the recent row that has been selected
        if new_card_id is None:
            new_card_id = 1
        else:
            new_card_id += 1
        cursor.execute(f'''INSERT INTO card (id, number, pin) VALUES
                          ({new_card_id}, '{new_card_num}', '{new_card_pin}');
                        ''')
        connection.commit()
    elif key == 2:
        is_card_valid = False
        card_num_passed = int(input("\nEnter your card number: \n"))  # type casting not that necessary
        card_pin_passed = int(input("Enter card PIN: \n"))

        cursor.execute(f'''SELECT 1 FROM card 
                                   WHERE number = '{card_num_passed}' AND pin = '{card_pin_passed}';''')
        if cursor.fetchone():
            is_card_valid = True
            cursor.execute(f'''SELECT id FROM card 
                                        WHERE number = '{card_num_passed}' AND pin = '{card_pin_passed}';''')
            current_id = cursor.fetchone()[0]
        else:
            pass
        if is_card_valid:
            is_logged = True
            print("\nYou have successfully logged in!\n")
            while is_logged:
                key_logged = int(input("1. Balance\n"
                                       "2. Add income\n"
                                       "3. Do transfer\n"
                                       "4. Close account\n"
                                       "5. Log out\n"
                                       "0. Exit\n"))
                if key_logged == 1:
                    print("\n")
                    #  list_of_accounts[current_account].show_balance()
                    #  want to use sql instead of reading from list
                    cursor.execute(f'''SELECT balance FROM card WHERE number = '{card_num_passed}';''')
                    print(f"Balance: {cursor.fetchone()[0]}")
                elif key_logged == 2:
                    deposit = int(input("\nEnter income:\n"))  # doesn't handle wacky input (np -100, strings etc.)
                    cursor.execute(f'''UPDATE card SET balance = balance + {deposit}
                                       WHERE number = '{card_num_passed}';''')
                    connection.commit()
                    print("Income was added!\n")
                elif key_logged == 3:
                    transfer_number_passed = int(input("Transfer\nEnter card number: \n"))
                    cursor.execute(f'''SELECT 0 FROM card WHERE number = '{transfer_number_passed}';''')
                    does_exist = cursor.fetchone()
                    if not is_luhn(f"{transfer_number_passed}"):
                        print("Probably you made a mistake in the card number. Please try again!")
                    elif transfer_number_passed == card_num_passed:
                        print("You can't transfer money to the same account!")
                    elif not does_exist:
                        print("Such a card does not exist.\n")
                    else:
                        transfer_money_passed = int(input("Enter how much money you want to transfer:\n"))
                        cursor.execute(f'''SELECT balance FROM card WHERE id = {current_id};''')
                        if transfer_money_passed > cursor.fetchone()[0]:
                            print("Not enough money!\n")
                        else:
                            cursor.execute(f'''UPDATE card SET balance = (balance - {transfer_money_passed}) 
                                               WHERE id = {current_id};''')
                            connection.commit()
                            cursor.execute(f'''UPDATE card SET balance = (balance + {transfer_money_passed}) 
                                               WHERE number = '{transfer_number_passed}';''')
                            connection.commit()

                elif key_logged == 4:
                    cursor.execute(f'''DELETE FROM card WHERE number = '{card_num_passed}'; ''')
                    connection.commit()
                    is_card_valid = False
                    is_logged = False
                    print("\nThe account has been closed!\n")
                elif key_logged == 5:
                    is_logged = False
                    is_card_valid = False
                    print("\nYou have successfully logged out!\n")
                elif key_logged == 0:
                    sys.exit("\nBye!")
                else:
                    pass
        else:
            print("\nWrong card number or PIN!\n")
    elif key == 0:
        sys.exit("\nBye!")
    elif key == 9:
        cursor.execute(f'''SELECT * FROM card;''')
        print(cursor.fetchall())
    else:
        pass
