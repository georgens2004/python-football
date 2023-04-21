import config
import pygame
from match.player import Player

class BotPlayer(Player):

    def set_box(self, box_corners):
        self.box_corners = box_corners
        self.box_center = [(box_corners[0][0] + box_corners[1][0]) // 2, (box_corners[0][1] + box_corners[1][1]) // 2]
    
    def set_initial_pos(self, initial_pos):
        self.initial_pos = initial_pos
        self.pos = initial_pos

    def restart(self):
        self.pos = self.initial_pos
        self.ball = None
    
    def is_bot_inside_box(self):
        if self.pos[0] < self.box_corners[0][0] or self.box_corners[1][0] < self.pos[0]:
            return False
        if self.pos[1] < self.box_corners[0][1] or self.box_corners[1][1] < self.pos[1]:
            return False
        return True
    
    def is_ball_inside_box(self, ball):
        if ball.pos[0] < self.box_corners[0][0] or self.box_corners[1][0] < ball.pos[0]:
            return False
        if ball.pos[1] < self.box_corners[0][1] or self.box_corners[1][1] < ball.pos[1]:
            return False
        return True
    
    def turn_to_box_center(self):
        self.dir = [self.box_center[0] - self.pos[0], self.box_center[1] - self.pos[1]]
        self.scale_dir()
    
    def stick_to_box_borders(self):
        if self.pos[0] < self.box_corners[0][0]:
            self.pos[0] = self.box_corners[0][0]
        elif self.pos[0] > self.box_corners[1][0]:
            self.pos[0] = self.box_corners[1][0]
        elif self.pos[1] < self.box_corners[0][1]:
            self.pos[1] = self.box_corners[0][1]
        elif self.pos[1] > self.box_corners[1][1]:
            self.pos[1] = self.box_corners[1][1]
    
    def get_nearest_teammate(self, team):
        nearest_teammate = None
        for player in team:
            dist = self.get_dist(player.pos)
            if player != self and config.BOT_MIN_DIST_TO_PASS < dist and (nearest_teammate is None or dist < self.get_dist(nearest_teammate.pos)):
                nearest_teammate = player
        return nearest_teammate
    
    def get_nearest_forward_teammate(self, team):
        nearest_teammate = None
        for player in team:
            dist = self.get_dist(player.pos)
            if player != self and ((self.pos[0] < player.pos[0]) ^ self.team) and config.BOT_MIN_DIST_TO_PASS < dist and (nearest_teammate is None or dist < self.get_dist(nearest_teammate.pos)):
                nearest_teammate = player
        return nearest_teammate
    
    def get_nearest_enemy(self, team):
        nearest_enemy = None
        for player in team:
            if nearest_enemy is None or self.get_dist(player.pos) < self.get_dist(nearest_enemy.pos):
                nearest_enemy = player
        return nearest_enemy
    
    def get_nearest_forward_enemy(self, team):
        nearest_enemy = None
        for player in team:
            if ((self.pos[0] < player.pos[0]) ^ self.team) and self.get_dist(player.pos) < config.BOT_STRIKER_DIST_TO_NOTICE_ENEMY and (nearest_enemy is None or self.get_dist(player.pos) < self.get_dist(nearest_enemy.pos)):
                nearest_enemy = player
        return nearest_enemy

    
    def is_team_has_ball(self, team):
        for player in team:
            if player.ball is not None:
                return True
        return False
    

class BotDefender(BotPlayer):

    def move_while_ball_is_away(self, ball):
        gates_center_y = (config.GATES[self.team][0][1] + config.GATES[self.team][1][1]) // 2
        great_pos_y = gates_center_y + (ball.pos[1] - gates_center_y) * (self.pos[0] - config.GATES[self.team][0][0]) / (ball.pos[0] - config.GATES[self.team][0][0])
        if self.pos[1] < great_pos_y - config.BOT_DISALLOWED_MOVE_RADIUS:
            self.turn_to([self.pos[0], self.pos[1] + 1])
            self.step()
        elif self.pos[1] > great_pos_y + config.BOT_DISALLOWED_MOVE_RADIUS:
            self.turn_to([self.pos[0], self.pos[1] - 1])
            self.step()
        self.stick_to_box_borders()
    
    def is_ball_near_gates(self, ball):
        return self.box_corners[0][0] < ball.pos[0] and ball.pos[0] < self.box_corners[1][0]
    
    def move_while_ball_is_near_gates(self, ball):
        gates_pos = config.GATES[self.team][self.class_number]
        great_pos_x = gates_pos[0] + (ball.pos[0] - gates_pos[0]) * (self.pos[1] - gates_pos[1]) / (ball.pos[1] - gates_pos[1])
        if self.pos[0] < great_pos_x - config.BOT_DISALLOWED_MOVE_RADIUS:
            self.turn_to([self.pos[0] + 1, self.pos[1]])
            self.step()
            self.turn_to(config.FIELD_CENTER)
        elif self.pos[0] > great_pos_x + config.BOT_DISALLOWED_MOVE_RADIUS:
            self.turn_to([self.pos[0] - 1, self.pos[1]])
            self.step()
            self.turn_to(config.FIELD_CENTER)
        self.stick_to_box_borders()

    def move(self, ball, team, enemy_team):
        if self.ball is not None:
            nearest_attacker = None
            for teammate in team:
                if teammate.player_class != "goalkeeper" and teammate.player_class != "defender" and (nearest_attacker is None or self.get_dist(teammate.pos) < self.get_dist(nearest_attacker.pos)):
                    nearest_attacker = teammate
            
            self.turn_to(nearest_attacker.pos)
            if self.get_dist(nearest_attacker.pos) < config.BOT_DEFENDER_DIST_TO_ATTACKER_TO_PASS:
                self.shoot()
            else:
                self.step()
        else:
            if not self.is_bot_inside_box():
                self.turn_to_box_center()
                self.step()
            elif self.is_ball_inside_box(ball):
                self.turn_to(ball.pos)
                self.step()
                self.stick_to_box_borders()
            elif self.is_ball_near_gates(ball):
                self.move_while_ball_is_near_gates(ball)
                self.stick_to_box_borders()
            else:
                self.move_while_ball_is_away(ball)
                self.stick_to_box_borders()

class BotWinger(BotPlayer):

    def move_while_ball_is_away(self, ball, team):
        if self.is_team_has_ball(team):
            self.dir = [config.GATES[1 - self.team][self.class_number][0] - self.pos[0], config.GATES[1 - self.team][self.class_number][1] - self.pos[1]]
            self.dir = [(self.dir[0] * 2 + ball.pos[0] - self.pos[0]) / 3, (self.dir[1] * 2 + ball.pos[1] - self.pos[1]) / 3]
            self.scale_dir()
        else:
            self.turn_to(ball.pos)
        self.step()
        self.stick_to_box_borders()

    def turn_to_post(self):
        self.dir = [config.GATES[1 - self.team][self.class_number][0] - self.pos[0], config.GATES[1 - self.team][self.class_number][1] - self.pos[1]]
        self.scale_dir()

    def move(self, ball, team, enemy_team):
        if self.ball is not None:
            if self.get_dist(config.GATES_CENTER[1 - self.team]) < config.BOT_WINGER_DIST_TO_SCORE:
                self.turn_to(config.GATES_CENTER[1 - self.team])
                self.shoot()
            nearest_teammate = self.get_nearest_teammate(team)
            nearest_enemy = self.get_nearest_enemy(enemy_team)
            if nearest_teammate is None:
                self.turn_to(config.GATES_CENTER[1 - self.team])
                self.shoot()
                return
            dist_to_teammate = self.get_dist(nearest_teammate.pos)
            if (config.BOT_WINGER_MIN_DIST_TO_TEAMMATE_TO_PASS < dist_to_teammate and dist_to_teammate < config.BOT_WINGER_MAX_DIST_TO_TEAMMATE_TO_PASS) or self.get_dist(nearest_enemy.pos) < config.BOT_WINGER_DANGEROUS_DIST_TO_ENEMY:
                self.turn_to(nearest_teammate.pos)
                self.shoot()
            else:
                self.turn_to_post()
                self.step()
        else:
            if not self.is_bot_inside_box():
                self.turn_to_box_center()
                self.step()
            elif self.is_ball_inside_box(ball):
                self.turn_to(ball.pos)
                self.step()
            else:
                self.move_while_ball_is_away(ball, team)


class BotStriker(BotPlayer):

    def move_while_ball_is_away(self, ball, team):
        if self.is_team_has_ball(team):
            self.dir = [config.GATES[1 - self.team][0][0] - self.pos[0], (config.GATES[1 - self.team][0][1] + config.GATES[1 - self.team][1][1]) // 2 - self.pos[1]]
            self.dir = [(self.dir[0] * 2 + ball.pos[0] - self.pos[0]) / 3, (self.dir[1] * 2 + ball.pos[1] - self.pos[1]) / 3]
            self.scale_dir()
        else:
            self.turn_to(ball.pos)
        self.step()
    
    def attack_with_ball(self, nearest_enemy):
        self.turn_to([self.pos[0] - (self.team * 2 - 1), self.pos[1]])
        if nearest_enemy is None:
            self.step()
            return
        height = nearest_enemy.pos[1] - self.pos[1]
        if abs(height) < config.BOT_STRIKER_DANGEROUS_ENEMY_HEIGHT:
            if height >= 0:
                # team 1: self.dir = [self.pos[0] - 1, self.pos[1] - 1]
                # team 0: self.dir = [self.pos[0] + 1, self.pos[1] - 1]
                self.turn_to([self.pos[0] - (self.team * 2 - 1), self.pos[1] - 1])
            else:
                self.turn_to([self.pos[0] - (self.team * 2 - 1), self.pos[1] + 1])
        self.step()
        
    
    def move(self, ball, team, enemy_team):
        if self.ball is not None:
            if self.get_dist(config.GATES_CENTER[1 - self.team]) < config.BOT_STRIKER_DIST_TO_SCORE:
                self.turn_to(config.GATES_CENTER[1 - self.team])
                self.shoot()
            nearest_teammate = self.get_nearest_forward_teammate(team)
            nearest_enemy = self.get_nearest_forward_enemy(enemy_team)
            if nearest_teammate is None:
                self.attack_with_ball(nearest_enemy)
                return
            dist_to_teammate = self.get_dist(nearest_teammate.pos)
            if (config.BOT_STRIKER_MIN_DIST_TO_TEAMMATE_TO_PASS < dist_to_teammate and dist_to_teammate < config.BOT_STRIKER_MAX_DIST_TO_TEAMMATE_TO_PASS) or self.get_dist(nearest_enemy.pos) < config.BOT_STRIKER_DANGEROUS_DIST_TO_ENEMY:
                self.turn_to(nearest_teammate.pos)
                self.shoot()
            else:
                self.turn_to(config.GATES_CENTER[1 - self.team])
                self.step()
        else:
            self.move_while_ball_is_away(ball, team)


class BotGoalkeeper(BotPlayer):

    def move_while_ball_is_away(self, ball):
        behind_gates_center_y = (config.GATES[self.team][0][1] + config.GATES[self.team][1][1]) // 2
        great_pos_y = behind_gates_center_y + (ball.pos[1] - behind_gates_center_y) * (self.pos[0] - 0) / (ball.pos[0] - 0)
        if self.pos[1] < great_pos_y - config.BOT_DISALLOWED_MOVE_RADIUS:
            self.turn_to([self.pos[0], self.pos[1] + 1])
            self.step()
        elif self.pos[1] > great_pos_y + config.BOT_DISALLOWED_MOVE_RADIUS:
            self.turn_to([self.pos[0], self.pos[1] - 1])
            self.step()
        self.stick_to_box_borders()
    
    def move(self, ball, team, enemy_team):
        if self.ball is not None:
            nearest_teammate = self.get_nearest_teammate(team)
            self.turn_to(nearest_teammate.pos)
            self.shoot()
        else:
            self.move_while_ball_is_away(ball)
