
import MoveTable

if __name__ == '__main__':
    ky = MoveTable.move_dictionary.keys()
    ky.sort()
    count = ky[-1] + 1
    output = [0]*count
    for k in ky:
        items = MoveTable.move_dictionary[k]
        sum = 0
        for m in items:
            sum |= (2**m)
        output[k] = sum
    out_file = open("condensed_table.py", "w")
    print >>out_file, "condensed_table = ", repr(output)


