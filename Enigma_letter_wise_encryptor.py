"""
Digital Enigma machine to encrypt and decrypt plane texts.
This Enigma machine encrypts a text file or a string, letter by letter.
If you want to encrypt different file format, check out Bit wise Enigma Encryptor.
"""
import os


class Rotor:
    def __init__(self, setting):
        """:param setting: A number between 0 to 94 specifying the initial potion of rotor."""
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
        if sockets: self.set_sockets(sockets)
        self.set_rotors(settings)

    def set_sockets(self, sockets):
        if len(set(sockets)) < 10: raise ValueError("Socket String must contain at least 10 Unique characters")
        temp_sockets = {}
        exponent = 1
        while len(temp_sockets) <= 100:
            for ind in range(0, len(sockets) - 1, 2):
                ord1 = self.generate_random(ord(sockets[ind]), exponent)
                ord2 = self.generate_random(ord(sockets[ind + 1]), exponent)
                if (ord1 in temp_sockets) or (ord2 in temp_sockets): continue
                temp_sockets[ord1] = ord2
                temp_sockets[ord2] = ord1
            exponent += 1
            if exponent == 1000: raise ValueError("Given String can`t be used as socket settings.")
        self.sockets = temp_sockets

    def set_rotors(self, settings):
        rotors = []
        for letter in str(settings):
            o1 = ord(letter)
            if o1 > 255: o1 = 255
            if o1 in rotors: continue
            rotors.append(o1)

        temp_rotors = []
        for setting in list(rotors):
            if not (0 < setting <= 255): raise ValueError("Given rotor setting has value out of (0 to 255) range.")
            temp_rotors.append(Rotor(setting))

        self.rotors = temp_rotors
        self.two_way_rotors = [*self.rotors, *[self.rotors[i] for i in range(len(self.rotors) - 2, -1, -1)]]

    def through_socket(self, letter):
        try:
            return self.sockets[letter]
        except KeyError:
            return letter

    def encrypt(self, message):
        tr = ""
        for letter in message:
            letter = self.through_socket(ord(letter))
            do_rotate = True
            for rotor in self.two_way_rotors:
                letter, do_rotate = rotor.encrypt(letter, do_rotate)
            tr += str(chr(self.through_socket(letter)))
        return tr

    def decrypt(self, message):
        tr = ""
        for letter in message:
            letter = self.through_socket(ord(letter))
            do_rotate = True
            for rotor in self.two_way_rotors:
                letter, do_rotate = rotor.decrypt(letter, do_rotate)
            tr += str(chr(self.through_socket(letter)))
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
        if os.path.isdir(f"{source_dir}\\{item}"): encrypt_folder(enigma, f"{source_dir}\\{item}", f"{target_dir}\\{item}")
        elif os.path.isfile(f"{source_dir}\\{item}"): encrypt_file(enigma, f"{source_dir}\\{item}", f"{target_dir}\\{item}.enc")


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
        if os.path.isdir(f"{source_dir}\\{item}"): decrypt_folder(enigma, f"{source_dir}\\{item}", f"{target_dir}\\{item}")
        elif os.path.isfile(f"{source_dir}\\{item}"): decrypt_file(enigma, f"{source_dir}\\{item}", f"{target_dir}\\{item.replace('.enc', '')}")




if __name__ == '__main__':
    engine = Engine((51, 47, 84), "this is just a test 123456789")
    # To encrypt a file use:
    # encrypt_file(engine, f"{file_path}\\{file_name}", f"{target_folder}\\{target_file}")
    # target_file need not to exist, file_path, file_name, target_folder must exist.
    # To encrypt a folder use:
    encrypt_folder(engine, r"D:\Tester\Chronicles", r"D:\ChronsEncrypted")

    # To decrypt a file use:
    # decrypt_file(engine, f"{file_path}\\{file_name}", f"{target_folder}\\{target_file}")
    # target_file need not to exist, file_path, file_name, target_folder must exist.
    # To decrypt a folder use:
    # decrypt_folder(engine, f"{folder_path}", f"{target_folder}")


