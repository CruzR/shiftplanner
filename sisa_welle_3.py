import itertools

_ID_COL = 0
_LASTNAME_COL = 4
_FIRSTNAME_COL = 5
_MINOR_COL = 34
_DEPARTMENTS_COL = 35
_MINOR_DEPARTMENTS_COL = 37
_SHIFTS_COL = 38
_MINOR_SHIFTS_COL = 40
_TROUBLESHOOTER_SHIFTS_COL = 41
_STAGEHAND_SHIFTS_COL = 42
_CAMPING_SHIFTS_COL = 43

def convert_row(r, departments, shifts, logger):
    isminor = False if r[_MINOR_COL] == 'Ja' else True
    if isminor:
        department_col = r[_MINOR_DEPARTMENTS_COL]
    else:
        department_col = r[_DEPARTMENTS_COL]
    desired_departments = []
    for name in department_col.split(', '):
        if name in departments:
            desired_departments.append(departments[name])
        else:
            app.logger.warn("Unknown department: {}".format(repr(name)))
    desired_shifts = []
    if isminor:
        shifts_col = r[_MINOR_SHIFTS_COL]
    else:
        shifts_col = r[_SHIFTS_COL]
    for dept, shift in itertools.product(department_col.split(', '), shifts_col.split(', ')):
        name = dept + " " + shift
        if name in shifts:
            desired_shifts.append(shifts[name])
        else:
            logger.warn("Unknown shift: {}".format(repr(name)))

    return {
        'id': int(r[_ID_COL]),
        'lastname': r[_LASTNAME_COL],
        'firstname': r[_FIRSTNAME_COL],
        'isminor': isminor,
        'assigned_shifts': [],
        'desired_departments': desired_departments,
        'desired_shifts': desired_shifts,
        'min_shifts': 2,
        'max_shifts': 2
    }
