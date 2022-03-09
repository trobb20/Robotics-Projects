from toothpaste_control import *

m = Motor('A')
squeeze = 0
baseurl = 'https://cad.onshape.com/documents/e61d2284326681e60c354303/w/06c3440ad86b926c4800c9f0/e/a34262dd0483af23abdb4057'
config = '?configuration=squeeze%3D{}%2Bmeter'

while True:
    user_input = str(input('Press h to home, e to extrude, q to quit: '))
    if user_input == 'h':
        home(m)
        squeeze = 0
    elif user_input == 'e':
        try:
            extrude_amount = int(input('How much to extrude? In mm: '))
        except Exception as e:
            print('Bad input.')
        else:
            new_squeeze = extrude_mm(m, -15, extrude_amount)
            squeeze = squeeze + new_squeeze
            print('You extruded %f mm3.'%volume_extruded(new_squeeze))
            print('See the tube:')
            print(baseurl+config.format(str(squeeze/1000)))
    elif user_input == 'q':
        print('Exiting.')
        break
    else:
        print('Bad input.')