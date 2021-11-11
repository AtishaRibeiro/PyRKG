from .Decomp import decode_RKG

class Inputs:

    def __init__(self):
        self.inputs = []

    def get_frame(self, index):
        return self.inputs[index]

    def get_total_frame_nr(self):
        return len(self.inputs)

    def read_ghost_file(self, file_name):
        with open(file_name, "rb") as f:
            src = f.read()
        raw_data = decode_RKG(src[0x8C:]) # remove the rkg header and decompress

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
            extra_frames = inputs & 0x0F 

            trick_inputs += [trick] * (frames + extra_frames)
            cur_byte += 2

        self.inputs = [(button_inputs[i][0], button_inputs[i][1], button_inputs[i][2], analog_inputs[i][0], analog_inputs[i][1], trick_inputs[i]) 
                        for i in range(len(button_inputs))]


if __name__ == "__main__":
    inputs = Inputs()
    inputs.read_ghost_file("01m08s7732250 Cole.rkg")
    print(len(inputs.inputs))