from cluedo.solver import *
import ipywidgets as widgets
from tabulate import tabulate
from IPython.display import HTML, display, display_html

tabulate.PRESERVE_WHITESPACE = True


class View(object):
    def __init__(self, cluedo):
        self.__cluedo = cluedo
        self.__history = []

    @property
    def cluedo(self):
        return self.__cluedo

    @property
    def history(self):
        return self.__history

    def display_suspects(self, player_assignments):
        suspects = [s.value for s in Suspect]
        player_names = []
        rows = []
        for suspect in suspects:
            row = [suspect]
            for player_name, player in player_assignments.items():
                player_names.append(player_name)
                value = player[Suspect][suspect]
                if value == {0}:
                    row.append("<font color='red'>&#10007</font>")
                elif value == {1}:
                    row.append("<font color='green'>&#10003</font>")
                else:
                    row.append("<font color='lightgray'>&ndash;</font>")
            rows.append(row)

        header_row = ['']
        header_row = header_row + player_names
        table = [header_row] + rows
        return tabulate(table,
                        tablefmt='html',
                        headers='firstrow',
                        stralign='right'
                        )

    def display_weapons(self, player_assignments):
        weapons = [w.value for w in list(Weapon)]
        player_names = []
        rows = []
        for weapon in weapons:
            row = [weapon]
            for player_name, player in player_assignments.items():
                player_names.append(player_name)
                value = player[Weapon][weapon]
                if value == {0}:
                    row.append("<font color='red'>&#10007</font>")
                elif value == {1}:
                    row.append("<font color='green'>&#10003</font>")
                else:
                    row.append("<font color='lightgray'>&ndash;</font>")
            rows.append(row)

        header_row = ['']
        header_row = header_row + player_names
        table = [header_row] + rows
        return tabulate(table,
                        tablefmt='html',
                        headers='firstrow',
                        stralign='right'
                        )

    def display_rooms(self, player_assignments):
        rooms = [r.value for r in list(Room)]
        player_names = []
        rows = []
        for room in rooms:
            row = [room]
            for player_name, player in player_assignments.items():
                player_names.append(player_name)
                value = player[Room][room]
                if value == {0}:
                    row.append("<font color='red'>&#10007</font>")
                elif value == {1}:
                    row.append("<font color='green'>&#10003</font>")
                else:
                    row.append("<font color='lightgray'>&ndash;</font>")
            rows.append(row)

        header_row = ['']
        header_row = header_row + player_names
        table = [header_row] + rows
        return tabulate(table,
                        tablefmt='html',
                        headers='firstrow',
                        stralign='right'
                        )

    def input(self):
        player_names = self.__cluedo.player_names
        player_names.remove(Cluedo.Player.Murderer)
        players = widgets.Select(
            options=['', *player_names],
            description='',
            disabled=False,
            layout=widgets.Layout(width='150px', height='100px')
        )

        booleans = widgets.Select(
            options=['', 'SOME_TRUE', 'ALL_FALSE'],
            description='',
            disabled=False,
            layout=widgets.Layout(width='150px', height='100px')
        )

        suspects = widgets.Select(
            options=['', *[s.value for s in Suspect]],
            description='',
            disabled=False,
            layout=widgets.Layout(width='150px', height='170px')
        )

        weapons = widgets.Select(
            options=['', *[w.value for w in Weapon]],
            description='',
            disabled=False,
            layout=widgets.Layout(width='150px', height='170px')
        )

        rooms = widgets.Select(
            options=['', *[r.value for r in Room]],
            description='',
            disabled=False,
            layout=widgets.Layout(width='150px', height='170px')
        )

        add = widgets.Button(
            description='Add',
            disabled=False,
            button_style='success',
            tooltip='Add',
        )

        run = widgets.Button(
            description='Run',
            disabled=False,
            button_style='success',
            tooltip='Run',
        )

        suspects_display = widgets.HTML(
            value="",
            placeholder='',
            description='',
            layout=widgets.Layout(width='30%', height='250')
        )

        weapons_display = widgets.HTML(
            value="",
            placeholder='',
            description='',
            layout=widgets.Layout(width='30%', height='250px')
        )

        rooms_display = widgets.HTML(
            value="",
            placeholder='',
            description='',
            layout=widgets.Layout(width='30%', height='250px')
        )

        hist_display = widgets.HTML(
            value="",
            placeholder='',
            description=''
        )

        time_limit = widgets.FloatSlider(
            value=60,
            min=0,
            max=500.0,
            step=1,
            description='Test:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='.1f',
        )

        def on_run_button_clicked(b):
            suspects_display.value = ""
            weapons_display.value = ""
            rooms_display.value = ""
            num_solutions = self.__cluedo.solve(time_limit=time_limit.value)
            # print(f"- possible solutions: {num_solutions}")
            # print(f"- solver time : {round(self.__cluedo.solver.WallTime(), 2)} seconds")
            player_assignments = self.__cluedo.players
            suspects_display.value = str(HTML(self.display_suspects(player_assignments)).data)
            weapons_display.value = self.display_weapons(player_assignments)
            rooms_display.value = self.display_rooms(player_assignments)
            # display_html(HTML(suspects_display.value))

        def on_add_button_clicked(b):

            constraints = []
            if suspects.value:
                constraints.append(Suspect(suspects.value))
            if weapons.value:
                constraints.append(Weapon(weapons.value))
            if rooms.value:
                constraints.append(Room(rooms.value))

            if not players.value or not booleans.value or len(constraints) == 0:
                return

            self.__history.append([players.value, booleans.value] + [c.value for c in constraints])
            value = ''
            for counter, row in enumerate(self.__history):
                value += f"<p><b>Turn {counter+1}:</b> {row}</p>"
            hist_display.value = value

            if booleans.value == 'SOME_TRUE':
                if len(constraints) == 1:
                    self.__cluedo.add_constraint(players.value, constraints[0])
                else:
                    self.__cluedo.add_or_constraint(players.value, constraints)
            elif booleans.value == 'ALL_FALSE':
                if suspects.value:
                    self.__cluedo.add_constraint(players.value, Suspect(suspects.value), False)
                if weapons.value:
                    self.__cluedo.add_constraint(players.value, Weapon(weapons.value), False)
                if rooms.value:
                    self.__cluedo.add_constraint(players.value, Room(rooms.value), False)

            players.value = ''
            booleans.value = ''
            suspects.value = ''
            weapons.value = ''
            rooms.value = ''

        add.on_click(on_add_button_clicked)
        run.on_click(on_run_button_clicked)

        return widgets.VBox(
            [widgets.HBox([widgets.VBox([widgets.Label('Players'), players]),
                           widgets.VBox([widgets.Label('Boolean Logic'), booleans]),
                           widgets.VBox([widgets.Label('Max Solver Time'), time_limit])
                           ],
                          ),
             widgets.HBox([widgets.VBox([widgets.Label('Suspects'), suspects]),
                           widgets.VBox([widgets.Label('Weapons'), weapons]),
                           widgets.VBox([widgets.Label('Rooms'), rooms])
                           ],
                          ),
             widgets.HBox([add, run]),
             widgets.HBox([suspects_display, weapons_display, rooms_display],
                          layout=widgets.Layout(width='100%', height='300px')
                          ),
             widgets.VBox([widgets.Label('Turn History'), hist_display])
             ])
