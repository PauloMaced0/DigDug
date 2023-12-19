from tree_search import SearchDomain

class DigDug(SearchDomain):
    def __init__(self, state):
        pass

    def actions(self, state):
        digdug_pos = state['digdug']
        level = state['level']
        game_map = state['map']
        rocks = [(rock['pos'][0], rock['pos'][1]) for rock in state['rocks']] 
        enemies = sorted(state["enemies"], key=lambda enemy : distance(digdug_pos, enemy['pos']) )
        closest_enemy = enemies[0]
        enemy_pos = closest_enemy['pos'] # Closest enemy
        enemy_distance = distance(digdug_pos, enemy_pos)
        colliding_enemies = [enemy for enemy in enemies if distance(digdug_pos, enemy['pos']) == 1 
                            and (digdug_pos[0],digdug_pos[1]) in calculate_next_position(state, enemy['pos'], enemy, rocks)] 
        x, y = state['digdug']
        list_of_actions = [(x - 1, y, 'a'), (x + 1, y, 'd'), (x, y + 1, 's'), (x, y - 1, 'w')]
        allowed_actions = []
        enemyes_cur_pos = [enemy['pos'] for enemy in enemies]
        enemies_next_pos = []
        deadend_positions = []
        for enemy in enemies:

            traverse = False
            if 'traverse' in enemy: traverse = True
            positions = calculate_next_position(state, enemy['pos'], enemy, rocks, traverse)
            for pos in positions:
                enemies_next_pos.append(pos)

            deadend_positions += verify_deadend(state['map'], enemy['pos'], enemy['dir'], rocks)

        possible_move = []
        fire_locations = predict_fygar_fire_locations(level, enemies, game_map)

        # Avoid collision with enemies or rocks current position
        for action in list_of_actions:
            # Rocks verification
            rock_in_front = False
            for r_x, r_y in rocks:
                if action[0] == r_x and action[1] == r_y:
                    rock_in_front = True
                    break 

            # Enemy next move verification
            enemy_in_front_next = False
            for e_x, e_y in enemies_next_pos:
                if(action[0] == e_x and action[1] == e_y):
                    enemy_in_front_next = True
                    break

            # Enemy current position verification1
            enemy_in_front = False
            for e_x, e_y in enemyes_cur_pos:
                if(action[0] == e_x and action[1] == e_y):
                    enemy_in_front = True
                    break
            if(enemy_in_front): possible_move.append(action)

            # Fire verification
            fire_in_front = False
            for fire_x, fire_y in fire_locations:
                if(action[0] == fire_x and action[1] == fire_y):
                    fire_in_front = True
                    break

            enemie_deadend = False

            for deadend_pos in deadend_positions:
                if action[:2] == deadend_pos:

                    enemie_deadend = True

            # If path is clear
            if(not rock_in_front and not enemy_in_front 
               and not fire_in_front and not enemy_in_front_next and not enemie_deadend):
                allowed_actions.append(action)

        allowed_actions_limit = []
        for action in allowed_actions:
            if 0 <= action[0] < 48 and 0 <= action[1] < 24:
                allowed_actions_limit.append(action)

        if enemy_distance <= 3 and is_aligned(state['digdug'], closest_enemy['pos'], state['digdug_dir']) \
                               and has_clear_path(digdug_pos, closest_enemy['pos'], state['map'], rocks) \
                               and (len(colliding_enemies) < 1 or (len(colliding_enemies) < 2 and closest_enemy in colliding_enemies)) \
                               and not rock_above(state):

            allowed_actions_limit.append((x, y, 'A'))
        
        if(not allowed_actions_limit): # Give him a possible move (Risky one) or just Pump in case we have no chance of moving
            if(possible_move):
                allowed_actions_limit += possible_move
            else:
                allowed_actions_limit.append((x, y, 'A'))

        return allowed_actions_limit 

    def result(self, state, action):
        new_state = state.copy()    
        new_state['digdug'] = [action[0], action[1]]

        new_state['key_action'] = action[2] 
        # If Digdug position changed -> Calculate Didgug Direction
        if state['digdug'] != new_state['digdug']:
            new_state['digdug_dir'] = calculate_digdug_direction(state['digdug'], new_state['digdug'])

        return new_state

    def cost(self, state, newstate):
        enemies = newstate['enemies']
        rocks = [(rock['pos'][0], rock['pos'][1]) for rock in state['rocks']] 
        x,y = newstate['digdug']

        enemies_next_pos = []
        for enemy in enemies:
            x2,y2 = calculate_next_position(state, enemy['pos'], enemy, rocks)[0]
            enemies_next_pos.append((x2,y2)) # 
            if(enemy['dir'] == newstate['digdug_dir']): # If im running from him
                x3,y3 = calculate_next_position(state, [x2,y2], enemy, rocks)[0]
                enemies_next_pos.append((x3, y3))
                x4,y4 = calculate_next_position(state, [x3,y3], enemy, rocks)[0]
                enemies_next_pos.append((x4, y4))

        if (x,y) in enemies_next_pos: # Add a cost to dodge from an enemy chasing us
            return 1

        return 0

    def heuristic(self, state):
        if not state['enemies']:
            return 0
        digdug = state['digdug']

        sorted_enemies = sorted(state["enemies"], key=lambda enemy : distance(digdug, enemy['pos']) )
        closest_enemy = sorted_enemies[0]
        closest_enemy_distance = distance(digdug, closest_enemy['pos'])

        if 'traverse' in closest_enemy: # We can be in Radius 2 (Calculated with Manhattan) but never in Radius 1 of a Traversing Pooka
            enemy_distance = distance(digdug, closest_enemy['pos'])
            if enemy_distance <= 2:
                return -enemy_distance-2

        # In case we are ready to shoot
        if(state['key_action'] == 'A'):
            return -2

        if(closest_enemy_distance < 5): # Face enemy before we are in range
            if(face_enemy(state, previous_position(digdug, state['key_action']), closest_enemy) == state['key_action']):
                return -1
            
        if move_inside_cave(state): # Don't dig unecessary blocks
            return closest_enemy_distance - 1

        return closest_enemy_distance

    def satisfies(self, state, goal):  
        digdug = state['digdug']
        digdug_pos = state['digdug']
        enemies = sorted(state["enemies"], key=lambda enemy : distance(digdug_pos, enemy['pos']) )
        closest_enemy = enemies[0]
        closest_enemy_distance = distance(digdug, closest_enemy['pos'])

        if 'key_action' not in state: 
            return False

        if 'traverse' in closest_enemy or state['key_action'] == 'A':
            return True
        
        # Objective: Get near enemy
        return closest_enemy_distance <= 3


def is_aligned(my_pos, enemy_pos, my_direction):
    x1, y1 = my_pos
    x2, y2 = enemy_pos

    if x1 == x2:
        return (y1 < y2 and my_direction == 2) or (y1 > y2 and my_direction == 0)

    elif y1 == y2:
        return (x1 < x2 and my_direction == 1) or (x1 > x2 and my_direction == 3)

    return False

def face_enemy(state, my_pos, enemy):
    x1, y1 = my_pos
    x2,y2 = enemy['pos']
    enemy_dir = enemy['dir']

    # If already in the same X just move vertically
    if(x1 == x2):
        if y1 < y2:
            return "s"  # Move down
        elif y1 > y2:
            return "w"  # Move up
    # If already in the same Y just move horizontally
    elif(y1 == y2):
        if x1 < x2:
            return "d"  # Move right
        elif x1 > x2:
            return "a"  # Move left
    # Else dont align your self with the enemy
    elif(abs(x2-x1) > abs(y2-y1)):
        if y1 < y2:
            return "s"  # Move down
        elif y1 > y2:
            return "w"  # Move up
    elif(abs(x1-x1) < abs(y2-y1)):
        if x1 < x2:
            return "d"  # Move right
        elif x1 > x2:
            return "a"  # Move left
    else:
        if(enemy_dir == 0 or enemy_dir == 2): # up or down
            if x1 < x2:
                return "d"  # Move right
            elif x1 > x2:
                return "a"  # Move left
        elif(enemy_dir == 1 or enemy_dir == 3): # right or left
            if y1 < y2:
                return "s"  # Move down
            elif y1 > y2:
                return "w"  # Move up
        else:
            return "A"  # Don't move


def has_clear_path(digdug_pos, enemy_pos, game_map, rocks):
    x1, y1 = digdug_pos
    x2, y2 = enemy_pos
    dist = distance(digdug_pos, enemy_pos)
    if x1 == x2:  # Same X, check vertical line
        step_y = 1 if y1 < y2 else -1
        for i in range(1, dist+1):
            if (x1, y1 + i * step_y) in rocks:
                return False
            if game_map[x1][y1 + i * step_y] == 1:
                return False
        return True
    elif y1 == y2:  # Same Y, check horizontal line
        step_x = 1 if x1 < x2 else -1
        for i in range(1, dist+1): 
            if (x1 + i * step_x, y1) in rocks:
                return False
            if game_map[x1 + i * step_x][y1] == 1:
                return False
        return True
    return False

def calculate_next_position(state, position, enemy, rocks, traverse=False):
    x, y = position
    level = state['level']
    digdug = state['digdug']
    direction = enemy['dir']
    name = enemy['name']
    if 'traverse' in enemy:
        traverse = True

    direction_changes = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    new_position = [(x + direction_changes[direction][0], y + direction_changes[direction][1])]
    if level >= 14 or traverse == True:
        DIRECTIONS = [0,1,2,3]
        fx, fy = enemy['pos']
        possible_moves = [
                pos
                for pos in [
                    calc_pos(position, d) for d in DIRECTIONS if name == 'Pooka' or (d == direction)
                ]
                if pos not in [position]
                and pos not in rocks
        ]
        next_move = sorted(possible_moves, key=lambda pos: distance_euclidean(pos, digdug))
        new_position += next_move
    return new_position 


def verify_deadend(map_grid, enemy_pos, enemy_dir, rocks): 
    next_pos = calc_pos(enemy_pos, enemy_dir)
    pointing_x, pointing_y = next_pos
    if(next_pos != enemy_pos and map_grid[pointing_x][pointing_y] == 0 and next_pos not in rocks): # Not a deadend
        return () 

    direction_changes = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    x, y = enemy_pos 
    possible_moves = []

    for dx, dy in direction_changes:
        nx, ny = x + dx, y + dy
        # Check if the next position is within the grid and is a path
        if 0 <= nx < 48 and 0 <= ny < 24 and map_grid[nx][ny] == 0 and (nx, ny) not in rocks:
            possible_moves.append((nx, ny))

    return possible_moves

def predict_fygar_fire_locations(level, enemies, game_map): #TODO check game
    return [
        [fygar_position[0] + i, fygar_position[1]]
        for enemy in enemies
        if enemy['name'] == 'Fygar'
        for fygar_position in [enemy['pos']]
        for i in range(1, 5)
        if level >= 14 \
        or(enemy['dir'] == 1 and (fygar_position[0] + i) < 48 \
                             and game_map[fygar_position[0] + i][fygar_position[1]] == 0) \
        or(enemy['dir'] == 2 and (fygar_position[1] + 1) < 24 \
                             and game_map[fygar_position[0]][fygar_position[1] + 1] == 1) \
        or(enemy['dir'] == 3 and (fygar_position[0] - 1) >= 0 \
                             and game_map[fygar_position[0] - 1][fygar_position[1]] == 1) \
        or(enemy['dir'] == 0 and (fygar_position[1] - 1) >= 0 \
                             and game_map[fygar_position[0]][fygar_position[1] - 1] == 1) # Right or facing a wall
    ] + [
        [fygar_position[0] - i, fygar_position[1]]
        for enemy in enemies
        if enemy['name'] == 'Fygar'
        for fygar_position in [enemy['pos']]
        for i in range(1, 5)
        if level >= 14 \
        or(enemy['dir'] == 3 and (fygar_position[0] - i) >= 0 \
                             and game_map[fygar_position[0] - i][fygar_position[1]] == 0) \
        or(enemy['dir'] == 2 and (fygar_position[1] + 1) < 24 \
                             and game_map[fygar_position[0]][fygar_position[1] + 1] == 1) \
        or(enemy['dir'] == 1 and (fygar_position[0] + 1) < 48 \
                             and game_map[fygar_position[0] + 1][fygar_position[1]] == 1) \
        or(enemy['dir'] == 0 and (fygar_position[1] - 1) >= 0 \
                             and game_map[fygar_position[0]][fygar_position[1] - 1] == 1)# Left
    ]

def rock_above(state):
    x, y = state['digdug']
    return any(rx == x and ry == y - 1 for rx, ry in (rock['pos'] for rock in state['rocks']))

def distance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

def distance_euclidean(point1, point2):
    return int(((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5)

def calculate_digdug_direction(current_position, previous_position) -> int:
    curr_x, curr_y = current_position
    prev_x, prev_y = previous_position

    if curr_x == prev_x:
        return 2 if curr_y > prev_y else 0
    elif curr_y == prev_y:
        return 1 if curr_x > prev_x else 3
    return -1

def move_inside_cave(state):
    x,y = state['digdug']
    game_map = state['map']

    # Position from new state is dug?
    return game_map[x][y] == 0

def previous_position(digdug, key):
    x,y = digdug
    if key == 'a':
        x += 1
    elif key == 'd':
        x -= 1
    elif key == 's':
        y -= 1
    elif key == 'w':
        y += 1

    return [x,y]


def calc_pos(cur, direction):
        cx, cy = cur
        npos = cur
        if direction == 0:
            npos = cx, cy - 1
        if direction == 1:
            npos = cx + 1, cy
        if direction == 2:
            npos = cx, cy + 1
        if direction == 3:
            npos = cx - 1, cy

        # test blocked
        if npos[0] < 0 or npos[0] >= 48 or npos[1] < 0 or npos[1] >= 24: # out of map boundaries
            return cur

        return npos
