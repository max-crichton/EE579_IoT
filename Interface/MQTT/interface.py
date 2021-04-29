import PySimpleGUI as sg
import pickle
from device import Device
from groups import Group

sg.theme('BrownBlue')
# Groups/Topics
# groups = {'Group 1': ['Light 1', 'Light 2', 'Controller 1'],
#           'Group 2': ['Temperature', 'RGB', 'Controller 2']}
groups = {}
# groups_test = {}
# groups = {'Group 1': []}
devices = {}

# Input and Output Peripherals
Input = ['Button', 'Potentiometer', 'Temperature Sensor']
Output = ['LED', 'RGB', 'Buzzer']


def load():
    """ Unpickle a file of pickled data. """
    with open('groups.pkl', "rb") as f:
        while True:
            try:
                groups = yield pickle.load(f)
            except EOFError:
                break
    return groups


def save():
    with open('groups.pkl', 'wb') as output:  # Overwrites any existing file.
        pickle.dump(groups, output, pickle.HIGHEST_PROTOCOL)


def new_device():
    i_col = [[]]
    for i in Input:
        i_col.append([sg.Checkbox(i, size=(20, 1), key='-in' + i + '-')])

    o_col = [[]]
    for i in Output:
        o_col.append([sg.Checkbox(i, size=(20, 1), key='-out' + i + '-')])

    k = []
    for keys, values in groups.items():
        k.append(keys)

    layout = [[sg.Text('Name:', pad=(0, 10)), sg.InputText('', key='-name-')],
              [sg.Text('Group:', pad=(0, 10)), sg.InputCombo(k, key='-group-')],
              [sg.Column([[sg.Frame('Input', i_col), sg.Frame('Output', o_col)]])],
              [sg.Button('Add', pad=(20, 10)), sg.Cancel(pad=(20, 10))]]

    window = sg.Window("New Device", auto_size_text=True, auto_size_buttons=True, resizable=True,
                       layout=layout, default_element_size=(12, 1), default_button_element_size=(12, 1),
                       font=("Helvetica", 20))
    while True:
        event, values = window.read()
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            break
        if event == 'Add':
            # Make sure that neither Name or Group are empty
            if str(values['-name-']) == '' or str(values['-group-']) == '':
                sg.popup('You must fill in all forms!')
                continue

            name = str(values['-name-'])
            input = []
            output = []
            for i in Input:
                if values['-in' + i + '-'] is True:
                    input.append(i)

            for i in Output:
                if values['-out' + i + '-'] is True:
                    output.append(i)

            # print(name, group, input, output)
            new_dev = Device(name, input, output)
            devices[new_dev.name] = new_dev
            if not groups:
                groups[str(values['-group-'])] = new_dev.name
            else:
                groups[str(values['-group-'])].append(new_dev.name)

            # groups_test[str(values['-group-'])].add(new_dev)  # Add class Device to class Group
            save()
            break

    window.close()


def new_group():
    device_col = [[]]
    for i in devices:
        device_col.append([sg.Checkbox(i, size=(20, len(devices)), key='-d' + i + '-')])

    layout = [[sg.Text('Name:', pad=(0, 10)), sg.InputText('', key='-name-')],
              [sg.Column([[sg.Frame('Devices', device_col)]])],
              [sg.Button('Add', pad=(20, 10)), sg.Cancel(pad=(20, 10))]]

    window = sg.Window("New Group", auto_size_text=True, auto_size_buttons=True, resizable=True,
                       layout=layout, default_element_size=(12, 1), default_button_element_size=(12, 1),
                       font=("Helvetica", 20))
    while True:
        event, values = window.read()
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            break
        if event == 'Add':
            if values['-name-'] not in groups.keys():  # if the name is not already taken
                d_col = []
                for i in devices:       # loops through all devices
                    if values['-d' + i + '-'] is True:  # if a device is checked
                        if not any(d_col):      # if it's the first device
                            d_col = [i]           # add it as the primary
                        else:                   # if not
                            d_col.append(i)         # add it to the group

                groups[values['-name-']] = d_col  # add the group to the groups dictionary
                print(groups)
                # groups_test[values['-name-']] = Group(values['-name-'], d_col)
                break
            else:
                sg.popup('This Group Name is already being used.')

    window.close()


def group_column():
    column = [[]]
    for i in groups:
        column.append([sg.Text(str(i + ':'), key=str(i))])
        column.append([sg.Listbox(values=groups[i], size=(20, len(groups[i])), key='-g' + i + '-')])
    return column


def rename_group():
    # Get group names
    k = []
    for keys, values in groups.items():
        k.append(keys)

    # Make a window to rename the group
    event, values = sg.Window(str('Rename Group'), [
        [sg.Text('Select Group:'), sg.InputCombo(k, key='-group-')],
        [sg.Text('Enter new name:'), sg.InputText('', key='-new-')],
        [sg.Button('Submit'), sg.Button('Cancel')]], font=("Helvetica", 20),
                              default_element_size=(12, 1), default_button_element_size=(12, 1)).read(
        close=True)
    # If submitted, change names and refresh window
    if event == 'Submit':
        groups[values['-new-']] = groups.pop(values['-group-'])


def del_group():
    # Get group names
    k = []
    for keys, values in groups.items():
        k.append(keys)

    # Make a window to rename the group
    event, values = sg.Window(str('Delete Group'), [
        [sg.Text('Select Group:'), sg.InputCombo(k, key='-group-')],
        [sg.Button('Submit'), sg.Button('Cancel')]], font=("Helvetica", 20),
                              default_element_size=(12, 1), default_button_element_size=(12, 1)).read(
        close=True)
    # If submitted, change names and refresh window
    if event == 'Submit':
        sure = sg.popup_yes_no('Are you sure you would like to delete ' + values['-group-'] + '?')
        if sure == 'Yes':
            groups.pop(values['-group-'], None)


def rename_dev():
    # Get device names
    k = []
    for keys, values in devices.items():
        k.append(keys)

    # Make a window to rename the device
    event, values = sg.Window(str('Rename Device'), [
        [sg.Text('Select Device:'), sg.InputCombo(k, key='-devices-')],
        [sg.Text('Enter new name:'), sg.InputText('', key='-new-')],
        [sg.Button('Submit'), sg.Button('Cancel')]], font=("Helvetica", 20),
                              default_element_size=(12, 1), default_button_element_size=(12, 1)).read(
        close=True)
    # If submitted, change names and refresh window
    if event == 'Submit':
        devices[values['-new-']] = devices.pop(values['-devices-'])
        for key, val in groups.items():
            if values['-devices-'] in val:
                val.remove(values['-devices-'])
                val.append(values['-new-'])
                groups[key] = val


def del_dev():
    # Get group names
    k = []
    for keys, values in devices.items():
        k.append(keys)

    # Make a window to rename the group
    event, values = sg.Window(str('Delete Device'), [
        [sg.Text('Select Device:'), sg.InputCombo(k, key='-device-')],
        [sg.Button('Submit'), sg.Button('Cancel')]], font=("Helvetica", 20),
                              default_element_size=(12, 1), default_button_element_size=(12, 1)).read(
        close=True)
    # If submitted, change names and refresh window
    if event == 'Submit':
        sure = sg.popup_yes_no('Are you sure you would like to delete ' + values['-device-'] + '?')
        if sure == 'Yes':
            devices.pop(values['-devices-'])
            for key, val in groups.items():
                if values['-devices-'] in val:
                    val.remove(values['-devices-'])
                    groups[key] = val


def main():
    # Menu Definition
    menu_def = [['New', ['New Device', 'New Group']], ['Edit', ['Rename', ['Group::R', 'Device::R'],
                                                                'Delete', ['Group::D', 'Device::D']]]]
    #groups = load()
    if not groups:
        layout = [[sg.Menu(menu_def, tearoff=False, key='-Menu-', font=("Helvetica", 12))],
                  [sg.Text('No Groups or Devices have been added.')],
                  [sg.Text('Add a Group or Device through the Menu')]]
    else:
        # Make the column containing the Groups and Devices
        column_1 = group_column()

        layout = [[sg.Menu(menu_def, tearoff=False, key='-Menu-', font=("Helvetica", 12))],
                  [sg.Column([[sg.Frame('', column_1, key='-Groups-')]])],
                  [sg.Button("OK", pad=(0, 10))]]

    # Create the window
    window = sg.Window("Main Interface", auto_size_text=True, auto_size_buttons=True, resizable=True,
                       layout=layout, default_element_size=(12, 1), default_button_element_size=(12, 1),
                       size=(800, 500), font=("Helvetica", 20))

    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "OK" or event == sg.WIN_CLOSED:
            save()
            break

        if event == 'New Device':
            new_device()
            for i in groups:
                window.Element('-g' + i + '-').Update(values=groups[i])
            main()

        if event == 'New Group':
            new_group()
            main()  # Refresh the interface
            break

        if event == 'Group::R':
            rename_group()
            main()
            break

        if event == 'Group::D':
            del_group()
            main()
            break

        if event == 'Device::R':
            rename_dev()
            main()
            break
        if event == 'Device::D':
            del_dev()
            main()
            break

    save()
    window.close()

if __name__ == "__main__":
    main()
