"""
Digital Enigma machine to encrypt and decrypt all types of files.
This Enigma machine encrypts a file bit by bit so it can encrypt every file type there can be.
Since, this is bit-by-bit-encryption, it is more secure than stander letter-by-letter-encryption.
How secure?
There are only 26 letters (94 including all the symbols on standard keyboard.) but there are 256 bits.
On physical Enigma machine, you get 5 rotors, out of which you choose 3, but here there is no limit on number of rotors.
On physical Enigma machine, you get 10 sockets, but here you have 100 sockets.
Including all the factors, theoretically, there can be infinite possible combinations,
To make it even harder to decrypt:
    There are two passwords, and the thief must guess both of them correctly at the same time.
    The passwords are not saved anywhere but in your brain`s memory, thus impossible to steel.
    The thief would either have to guess the password, or to test all the possible passwords one by one until he found both the passwords.
    Guessing the password is possible but there is no way of telling if he guessed one password wrong or both, and if one password is wrong there is no way to tell which one.
    And if he tries to check every possible combination, then he will have to enter the password, decrypt a file and check if the file is readable or not.
    Checking if the file is readable or not takes minimum of one second. That means, he can`t guess millions of passwords every seconds, infact
    he can check only one password per second which makes checking every password approach extremely slow.
"""
import os


class Rotor:
    def __init__(self, setting):
        """:param setting: A number between 0 to 255 specifying the initial potion of rotor."""
        self.initial_setting = setting
        self.rotor_size = 256
        self.wheel_indices = [*range(setting, self.rotor_size), *range(setting)]

    def rotate(self):
        """
        :return: True if rotor has finished the revolution else False
        """
        self.wheel_indices = [*self.wheel_indices[1:], self.wheel_indices[0]]
        if self.initial_setting == self.wheel_indices[0]: return True
        return False

    def encrypt(self, letter, rotate=True):
        tr = self.wheel_indices[letter]
        revolution_complete = False
        if rotate: revolution_complete = self.rotate()
        return tr, revolution_complete

    def decrypt(self, letter, rotate=True):
        tr = self.wheel_indices.index(letter)
        revolution_complete = False
        if rotate: revolution_complete = self.rotate()
        return tr, revolution_complete

    def reset(self):
        self.wheel_indices = [*range(self.initial_setting, self.rotor_size), *range(0, self.initial_setting)]

    def set(self, new_setting=0):
        self.initial_setting = new_setting
        self.reset()


class Engine:
    def __init__(self, settings=(0, 0, 0), sockets=""):
        """
        :param settings: String or a Tuple with each element in range of 0, 255
        :param sockets: must be a string with at least 10 unique characters.
        """
        self.settings = settings
        if sockets: self.set_sockets(sockets)
        self.set_rotors(settings)

    def __str__(self):
        return f"Enigma Settings: {self.settings}\nEnigma Sockets: {self.sockets}"

    def set_sockets(self, sockets):
        if len(set(sockets)) < 10: raise ValueError("Socket String must contain at least 10 Unique characters")
        self.sockets = {}
        exponent = 1
        while len(self.sockets) <= 100:
            for ind in range(0, len(sockets) - 1, 2):
                ord1 = self.generate_random(ord(sockets[ind]), exponent)
                ord2 = self.generate_random(ord(sockets[ind + 1]), exponent)
                if (ord1 in self.sockets) or (ord2 in self.sockets): continue
                self.sockets[ord1] = ord2
                self.sockets[ord2] = ord1
            exponent += 1

    def set_rotors(self, settings):
        rotors = []
        if type(settings) is str:
            for letter in str(settings):
                o1 = ord(letter)
                if o1 > 255: o1 = 255
                if o1 in rotors: continue
                rotors.append(int(o1))
        elif type(settings) is tuple:
            for o1 in settings:
                if o1 > 255: raise ValueError("Given rotor settings has integers out of (0, 255) range.")
                if o1 in rotors: continue
                rotors.append(int(o1))

        self.rotors = []
        for setting in list(rotors):
            self.rotors.append(Rotor(setting))
        self.two_way_rotors = [*self.rotors, *[self.rotors[i] for i in range(len(self.rotors) - 2, -1, -1)]]

    def through_socket(self, letter):
        try:
            return self.sockets[letter]
        except KeyError:
            return letter

    def encrypt(self, message):
        tr = []
        for letter in message:
            letter = self.through_socket(letter)
            do_rotate = True
            for rotor in self.two_way_rotors:
                letter, do_rotate = rotor.encrypt(letter, do_rotate)
            tr.append(self.through_socket(letter))
        return tr

    def decrypt(self, message):
        tr = []
        for letter in message:
            letter = self.through_socket(letter)
            do_rotate = True
            for rotor in self.two_way_rotors:
                letter, do_rotate = rotor.decrypt(letter, do_rotate)
            tr.append(self.through_socket(letter))
        return tr

    def set(self, settings, sockets):
        self.set_sockets(sockets)
        self.rotors = []
        for setting in list(settings):
            self.rotors.append(Rotor(setting))

        self.two_way_rotors = [*self.rotors, *[self.rotors[i] for i in range(len(self.rotors) - 2, -1, -1)]]

    def reset(self):
        for rotor in self.rotors: rotor.reset()

    def generate_random(self, order, exponent):
        X = order
        for x in range(exponent): X = (7 * X + 13) % 255
        return X


def encrypt_file(enigma, source_file, target_file):
    enigma.reset()
    print("\t" + str(source_file))
    word_file = open(source_file, "rb")
    chrn_file = open(target_file, "wb")
    chrn_file.write(bytearray(enigma.encrypt(list(word_file.read()))))
    word_file.close()
    chrn_file.close()


def encrypt_folder(enigma, source_dir, target_dir):
    if not os.path.isdir(target_dir): os.mkdir(target_dir)
    for item in os.listdir(source_dir):
        if os.path.isdir(f"{source_dir}\\{item}"):
            encrypt_folder(enigma, f"{source_dir}\\{item}", f"{target_dir}\\{item}")
        elif os.path.isfile(f"{source_dir}\\{item}"):
            encrypt_file(enigma, f"{source_dir}\\{item}", f"{target_dir}\\{item}.enc")


def decrypt_file(enigma, source_file, target_file):
    print("\t" + str(source_file))
    enigma.reset()
    chrn_file = open(source_file, "rb")
    word_file = open(target_file, "wb")
    word_file.write(bytearray(enigma.decrypt(list(chrn_file.read()))))
    chrn_file.close()
    word_file.close()


def decrypt_folder(enigma, source_dir, target_dir):
    if not os.path.isdir(target_dir): os.mkdir(target_dir)
    for item in os.listdir(source_dir):
        if os.path.isdir(f"{source_dir}\\{item}"):
            decrypt_folder(enigma, f"{source_dir}\\{item}", f"{target_dir}\\{item}")
        elif os.path.isfile(f"{source_dir}\\{item}"):
            decrypt_file(enigma, f"{source_dir}\\{item}", f"{target_dir}\\{item.replace('.enc', '')}")


change = lambda option: "Good" if option else "Bad\t\t\t"


def check_file(enigma, master_file, child_file):
    master = open(master_file, "rb")
    try:
        child = open(child_file, "rb")
    except FileNotFoundError:
        print("Not Found ->    ", str(master_file))
        return
    print(change(master.read() == bytearray(enigma.decrypt(list(child.read())))), " ->    ", str(master_file))
    master.close()
    child.close()


def check_folder(enigma, master_folder, child_folder):
    for item in os.listdir(master_folder):
        if os.path.isdir(f"{master_folder}\\{item}"):
            check_folder(enigma, f"{master_folder}\\{item}", f"{child_folder}\\{item}")
        elif os.path.isfile(f"{master_folder}\\{item}"):
            check_file(enigma, f"{master_folder}\\{item}", f"{child_folder}\\{item}")


if __name__ == '__main__':
    source_folder = "source\\folder\\name\\here"
    source_file_name_with_extension = "source_file_name.extension"
    target_folder = "target\\folder\\name\\here"
    target_file_name_with_extension = "target_file_name"  # no need of extension, this file may or may not exist.
    decrypted_folder = "decrypted\\folder\\name\\here"
    decrypted_file_with_extension = "decrypted_file_name.extension"
    engine = Engine((19, 45, 75), "This is a test123456789")

    # To Encrypt File, use:
    encrypt_file(engine, f"{source_folder}\\{source_file_name_with_extension}", f"{target_folder}\\{target_file_name_with_extension}")

    # To Encrypt Folder, use:
    # decrypt_folder(engine, source_folder, f"{target_folder}\\Encrypted")    # create a new directory to save Encrypted.

    # To Decrypt File, use:
    # decrypt_file(engine, f"{source_folder}\\{source_file_name_with_extension}", f"{target_folder}\\{target_file_name_with_extension}")

    # To Encrypt Folder, use:
    # decrypt_folder(engine, source_folder, f"{target_folder}\\Decrypted")    # create a new directory to save Decrypted.

    # To check if the file is properly encrypted or not, use:
    # check_file(engine, f"{source_folder}\\{source_file_name_with_extension}", f"{decrypted_folder}\\{decrypted_file_with_extension}")

    # To check if the folder is properly encrypted or not, decrypt the folder and then use:
    # check_folder(engine, source_folder, decrypted_folder)
