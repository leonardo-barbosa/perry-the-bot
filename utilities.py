def open_file():
    fl = open('queue_marker.txt', 'r+')
    return fl


def clear_n_write_file(fl, marker):
    fl.seek(0)
    fl.truncate()
    fl.write(str(marker))

def get_dates_diff_in_hours(d1, d2):
    diff = d1 - d2
    return (d1.days * 24) + (d2.seconds / 60 / 60)
