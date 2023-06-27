import csv
from math import floor
from .Decomp import decode_RKG


class Inputs:
    def __init__(self):
        self.inputs = []
        self.framerate = None

    def get_framerate(self):
        return self.framerate

    def get_frame(self, index):
        return self.inputs[index]

    def get_total_frame_nr(self):
        return len(self.inputs)

    def read_file(self, file_name):
        extension = file_name.split(".")[-1]
        if extension == "rkg":
            self.read_ghost_file(file_name)
            self.framerate = 59.94
        elif extension == "dtm":
            self.read_dtm(file_name)
            self.framerate = 180
        elif extension == "csv" or extension == "txt":
            self.read_tas_text_file(file_name)
            self.framerate = 59.94
        else:
            self.read_ghost_file(file_name)
            self.framerate = 59.94

    def read_ghost_file(self, file_name):
        with open(file_name, "rb") as f:
            src = f.read()
        raw_data = decode_RKG(src[0x8C:])  # remove the rkg header and decompress

        # header
        nr_button_inputs = (raw_data[0] << 0x8) | raw_data[1]
        nr_analog_inputs = (raw_data[2] << 0x8) | raw_data[3]
        nr_trick_inputs = (raw_data[4] << 0x8) | raw_data[5]

        # body
        button_inputs = []
        analog_inputs = []
        trick_inputs = []

        cur_byte = 8

        for _ in range(nr_button_inputs):
            inputs = raw_data[cur_byte]
            frames = raw_data[cur_byte + 1]
            accelerator = inputs & 0x1
            drift = (inputs & 0x2) >> 1
            item = (inputs & 0x4) >> 2

            button_inputs += [(accelerator, drift, item)] * frames
            cur_byte += 2

        for _ in range(nr_analog_inputs):
            inputs = raw_data[cur_byte]
            frames = raw_data[cur_byte + 1]
            vertical = inputs & 0xF
            horizontal = (inputs >> 4) & 0xF

            analog_inputs += [(vertical, horizontal)] * frames
            cur_byte += 2

        for _ in range(nr_trick_inputs):
            inputs = raw_data[cur_byte]
            frames = raw_data[cur_byte + 1]
            trick = (inputs & 0x70) >> 0x4
            extra_frames = (inputs & 0x0F) << 0x8

            trick_inputs += [trick] * (frames + extra_frames)
            cur_byte += 2

        self.inputs = [
            (
                button_inputs[i][0],
                button_inputs[i][1],
                button_inputs[i][2],
                analog_inputs[i][0],
                analog_inputs[i][1],
                trick_inputs[i],
            )
            for i in range(len(button_inputs))
        ]

    # credit: https://github.com/APerson13/DTM-To-Txt
    def read_dtm(self, file_name):
        with open(file_name, "rb") as f:
            f.seek(0x100)
            while True:
                try:
                    byte_list = list(f.read(8))
                    assert len(byte_list) == 8
                    # `input_list` contains the following set of inputs in order:
                    # START, A, B, X, Y, Z, UP, DOWN, LEFT, RIGHT, L, R, change disc, reset, nothing, nothing
                    input_list = self._decode_bitfield(byte_list[0], 8)
                    input_list.extend(self._decode_bitfield(byte_list[1], 8))

                    trick = 0
                    if input_list[6] == 1:
                        trick = 1
                    elif input_list[7] == 1:
                        trick = 2
                    elif input_list[8] == 1:
                        trick = 3
                    elif input_list[9] == 1:
                        trick = 4
                    directional = (
                        floor((int(byte_list[5]) - 1) / (254 / 14)),
                        floor((int(byte_list[4]) - 1) / (254 / 14)),
                    )
                    self.inputs.append(
                        (
                            str(input_list[1]),
                            str(input_list[2] | input_list[11]),
                            str(input_list[10]),
                            directional[0],
                            directional[1],
                            str(trick),
                        )
                    )
                except AssertionError:
                    break

    def _decode_bitfield(self, bitfield: int, return_length: int):
        output_list = []
        for i in range(return_length):
            output_list.append(bitfield & 1)
            bitfield >>= 1  # This will make a list of least to most significant bits.
        return output_list

    def read_tas_text_file(self, file_name):
        with open(file_name, "r") as f:
            reader = csv.reader(f)
            for line in reader:
                if len(line) < 6:
                    raise Exception(f"Malformed line in text file: {line}")
                self.inputs.append(
                    [
                        int(line[0]),
                        int(line[1]),
                        int(line[2]),
                        int(line[4]) + 7,
                        int(line[3]) + 7,
                        int(line[5]),
                    ]
                )


if __name__ == "__main__":
    inputs = Inputs()
    inputs.read_ghost_file("01m08s7732250 Cole.rkg")
    print(len(inputs.inputs))
