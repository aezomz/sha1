__all__ = ['sha1', 'truncate_front', 'binary_addition', 'left_rotate', 'chunking',
           'binary_pad']

def sha1(text):
    # initial sha values 5 32 bits
    h0 = '01100111010001010010001100000001'
    h1 = '11101111110011011010101110001001'
    h2 = '10011000101110101101110011111110'
    h3 = '00010000001100100101010001110110'
    h4 = '11000011110100101110000111110000'

    # convert each letter to ascii standard
    ascii_text = [ord(letter) for letter in text]

    # binary each value and slice from 2 to remove python binary prefix "0b", fill to ensure 8 bits
    binary_8bit = [binary_pad(ascii, 8) for ascii in ascii_text]

    # add 1 at the end to mark start of padding as we need to pad to 512 bits
    # its to indicate that the content ended there, we add length of the content later on
    binary_string = ''.join(binary_8bit) + '1'

    # essentially to loop till 448 bits filled with zero
    # saving 64 bits for length in binary
    while len(binary_string) % 512 != 448:
        binary_string += '0'

    ascii_string_length = len(''.join(binary_8bit))
    # get the length representation in binary and put it in the back of 512 bits
    # as binary string length will never exceed 2^64 -1
    binary_string_length_padded = binary_pad(ascii_string_length, 64)
    binary_string += binary_string_length_padded

    chunks = chunking(binary_string, 512)

    # split into 16 words of size 32 bits each
    words = [chunking(chunk, 32) for chunk in chunks]

    # extend the 16 words into 80 words by appending result after algo
    for array in words:
        for i in range(16, 80):
            word_a = array[i - 3]
            word_b = array[i - 8]
            word_c = array[i - 14]
            word_d = array[i - 16]

            xor_a = binary_pad(int(word_a, 2) ^ int(word_b, 2))
            xor_b = binary_pad(int(xor_a, 2) ^ int(word_c, 2))
            xor_c = binary_pad(int(xor_b, 2) ^ int(word_d, 2))

            left_rotated = left_rotate(xor_c, 1)

            array.append(left_rotated)

    # after extending each sub array to 80
    # its time to update the initial hash values
    for i in range(0, len(words)):
        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        for j in range(0, 80):
            if j < 20:
                b_and_c = binary_pad(int(b, 2) & int(c, 2))
                not_b = binary_pad(~int(b, 2) & int(d, 2))
                f = binary_pad(int(b_and_c, 2) | int(not_b, 2))
                k = '01011010100000100111100110011001'
            elif j < 40:
                b_xor_c = binary_pad(int(b, 2) ^ int(c, 2))
                f = binary_pad(int(b_xor_c, 2) ^ int(d, 2))
                k = '01101110110110011110101110100001'

            elif j < 60:
                b_and_c = binary_pad(int(b, 2) & int(c, 2))
                b_and_d = binary_pad(int(b, 2) & int(d, 2))
                c_and_d = binary_pad(int(c, 2) & int(d, 2))
                b_and_c_or_b_and_d = binary_pad(int(b_and_c, 2) | int(b_and_d, 2))
                f = binary_pad(int(b_and_c_or_b_and_d, 2) | int(c_and_d, 2))
                k = '10001111000110111011110011011100'

            else:
                b_xor_c = binary_pad(int(b, 2) ^ int(c, 2))
                f = binary_pad(int(b_xor_c, 2) ^ int(d, 2))
                k = '11001010011000101100000111010110'

            word = words[i][j]
            temp_a = binary_addition(left_rotate(a, 5), f)
            temp_b = binary_addition(temp_a, e)
            temp_c = binary_addition(temp_b, k)
            temp = binary_addition(temp_c, word)

            # not sure if will encounter self inference problem
            temp = truncate_front(temp, 32)
            e = d
            d = c
            c = left_rotate(b, 30)
            b = a
            a = temp
        
        h0 = truncate_front(binary_addition(h0, a), 32)
        h1 = truncate_front(binary_addition(h1, b), 32)
        h2 = truncate_front(binary_addition(h2, c), 32)
        h3 = truncate_front(binary_addition(h3, d), 32)
        h4 = truncate_front(binary_addition(h4, e), 32)
    
    # convert to hex format and concat them together to product 160 bits hash    
    result = [f'{int(binary_value, 2):x}' for binary_value in [h0, h1, h2, h3, h4]]
    return ''.join(result)


def truncate_front(value_string, length):
    '''drop bit in the front until string of length'''
    while (len(value_string) > length):
        value_string = value_string[1:]
    return value_string

def binary_addition(x, y, no_bits = 0):
    '''convert to int for addition and convert back
       pad based on no_bits'''
    integer_sum = int(x, 2) + int(y, 2)
    sum = binary_pad(integer_sum, no_bits)

    # not too sure why there is this logic looks wrong to me
    # return '1' + sum if len(sum) == len(x) else sum
    # so am using this instead
    return sum

def left_rotate(value_string, x): 
    '''drop x bits from the left and join on the right'''
    return value_string[x:] + value_string[:x]

def chunking(value_string, chunk_size=512):
    '''Split long string into chunk size into a list'''
    value_length = len(value_string)
    return [value_string[i:i+chunk_size] for i in range(0, value_length, chunk_size)]

def binary_pad(value_string, no_bits = 32):
    '''Convert to binary and remove "0b" and pad to no_bits'''
    return bin(value_string)[2:].zfill(no_bits)

if __name__ == '__main__':
    print(sha1('hello world'))