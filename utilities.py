def open_file():
    fl = open('queue_marker.txt', 'r+')

    return fl


def clear_n_write_file(fl, marker):
    fl.seek(0)
    fl.truncate()
    fl.write(str(marker))
