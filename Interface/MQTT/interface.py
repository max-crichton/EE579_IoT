import PySimpleGUI as sg
from device import Device
from groups import Groups

sg.theme('BrownBlue')
# Groups/Topics
groups = {'Group 1': ['Light 1', 'Light 2', 'Controller 1'],
          'Group 2': ['Temperature', 'RGB', 'Controller 2']}
# groups = {'Group 1': []}
devices = {}

# Input and Output Peripherals
Input = ['Button', 'Potentiometer', 'Temperature Sensor']
Output = ['LED', 'RGB', 'Buzzer']


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
            name = str(values['-name-'])
            input = []
            output = []
            for i in Input:
                if values['-in' + i + '-'] is True:
                    input.append(i)
            if not input:
                input = 0
            for i in Output:
                if values['-out' + i + '-'] is True:
                    output.append(i)
            if not output:
                output = 0
            # print(name, group, input, output)
            new_dev = Device(name, input, output)
            devices[new_dev.name] = new_dev
            groups[str(values['-group-'])].append(new_dev.name)
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
            if values['-name-'] not in groups.keys():
                d_col = [[]]
                for i in devices:
                    if values['-d' + i + '-'] is True:
                        if not any(d_col):
                            print('empty', i)
                            d_col = [[i]]
                        else:
                            print(i)
                            d_col.append(i)

                groups[values['-name-']] = d_col
                break
            else:
                sg.popup('This Group Name is already being used.')

    window.close()


def group_column():
    column = [[]]
    for i in groups:
        column.append([sg.Text(str(i + ':'))])
        column.append([sg.Listbox(values=groups[i], size=(20, len(groups[i])), key='-g' + i + '-')])
    return column


def main():
    # Menu Definition
    menu_def = [['New', ['New Device', 'New Group']]]

    # Make the column containing the Groups and Devices
    column_1 = group_column()

    layout = [[sg.Menu(menu_def, tearoff=False, key='-Menu-')],
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
            break

        if event == 'New Device':
            new_device()
            for i in groups:
                window.Element('-g' + i + '-').Update(values=groups[i])

        if event == 'New Group':
            new_group()
            main()  # Refresh the interface
            break

    window.close()


main()
