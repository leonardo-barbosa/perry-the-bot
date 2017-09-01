def open_file():
    file = open('queue_marker.txt', 'r+')

    return file


def clear_n_write_file(file, marker):
    file.seek(0)
    file.truncate()
    file.write(str(marker))
