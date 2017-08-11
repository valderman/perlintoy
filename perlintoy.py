#!/usr/bin/python3
import argparse
import pygame
import pygame.draw
import pygame.event
import pygame.font
import pygame.key
import pygame.time
import perlin

DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
DEFAULT_PAN_SPEED = 500
DEFAULT_SCALE = 1
PAN_EPSILON = 0.0001

class PerlinRenderer:
    '''Keeps track of Perlin noise settings and rendering.'''
    def __init__(self, width, height, scale, octaves, persistence):
        self._width = width
        self._height = height
        self._scale = scale
        self._octaves = octaves
        self._persistence = persistence
        self._gen = perlin.Perlin(self.octaves, self.persistence)

    @property
    def scale(self): return self._scale

    @property
    def octaves(self): return self._octaves

    @property
    def persistence(self): return self._persistence

    def _reloadGen(self):
        '''Recreate the noise generator with the current parameters.'''
        self._gen = perlin.Perlin(self.octaves, self.persistence)
          
    def modifyOctaves(self, diff):
        '''Add diff to the number of octaves of the generator, then reload it.'''
        self._octaves = max(1, self.octaves + diff)
        self._reloadGen()

    def modifyPersistence(self, diff):
        '''Add diff to the persistence of the generator, then reload it.'''
        self._persistence += diff
        self._reloadGen()

    def modifyXScale(self, diff):
        '''Add diff to the horizontal rendering scale.'''
        self._scale += diff

    def render(self, screen, offset):
        '''Render noise to the screen according to current settings, starting
           from the give offset.'''
        y0 = self._height/2
        halfHeight = self._height/2
        scale = 10*self._scale
        for x in range(0,self._width):
            y = self._gen.noise((x+offset)/scale)*halfHeight+halfHeight
            pygame.draw.line(screen, (0,0,0), (x, y0), (x+1, y))
            y0 = y

class TextRenderer:
    '''Renders lines of text into the screen.'''
    def __init__(self, font = "Courier New", size = 20):
        self._text_lines = []
        pygame.font.init()
        self._font = pygame.font.SysFont(font, size)

    def print(self, text):
        '''Append a line of text to the application's text buffer.
           It will be rendered to screen during the next screen update.'''
        self._text_lines.append(text)

    def render(self, screen, pos):
        '''Render all queued lines of text to the screen, then clear the
           text buffer.'''
        (x, y) = pos
        for line in self._text_lines:
            surface = self._font.render(line, False, (0,0,0))
            screen.blit(surface, (x, y))
            y += 25
        self._text_lines = []

class PerlinToy:
    def __init__(self,
                 width    = DEFAULT_WIDTH,
                 height   = DEFAULT_HEIGHT,
                 panSpeed = DEFAULT_PAN_SPEED):
        pygame.init()
        self._perlin = PerlinRenderer(width, height, 10, 2, 0.5)
        self._text = TextRenderer()
        self._done = False
        self._panSpeed = panSpeed
        self._lastPanTime = 0
        self._currentPanSpeed = 0
        self._isPanning = False
        self._offset = 0
        self._keyUpHandlers = {
            pygame.K_ESCAPE:   lambda: self._quit()
          , pygame.K_UP:       lambda: self._perlin.modifyOctaves(1)
          , pygame.K_DOWN:     lambda: self._perlin.modifyOctaves(-1)
          , pygame.K_PAGEUP:   lambda: self._perlin.modifyPersistence(0.1)
          , pygame.K_PAGEDOWN: lambda: self._perlin.modifyPersistence(-0.1)
          , pygame.K_HOME:     lambda: self._perlin.modifyXScale(5)
          , pygame.K_END:      lambda: self._perlin.modifyXScale(-5)
          , pygame.K_LEFT:     lambda: self._modifyPan(self._panSpeed)
          , pygame.K_RIGHT:    lambda: self._modifyPan(-self._panSpeed)
          }
        self._keyDownHandlers = {
            pygame.K_LEFT:  lambda: self._modifyPan(-self._panSpeed)
          , pygame.K_RIGHT: lambda: self._modifyPan(self._panSpeed)
          }

    def _quit(self):
        '''Set the exit flag, which will cause the program to terminate
           after the next render completes.'''
        self._done = True

    def _modifyPan(self, diff):
        '''Add diff to the pan speed of the screen.'''
        self._currentPanSpeed += diff
        self._isPanning = abs(self._currentPanSpeed) > PAN_EPSILON
        self._lastPanTime = 0

    def _render(self, screen):
        '''Clear the screen, then render the "scene".'''
        screen.fill((255, 255, 255))
        self._perlin.render(screen, self._offset)
        self._text.render(screen, (20, 20))
        pygame.display.flip()

    def _pan(self):
        '''Pan the view by _panSpeed units per second.'''
        if self._isPanning:
            t = pygame.time.get_ticks()
            if self._lastPanTime == 0:
                # If we just started panning...
                self._lastPanTime = t
            delta = t - self._lastPanTime
            if delta > 0:
                self._offset += (self._currentPanSpeed * delta)/1000
                self._lastPanTime = t

    def _handleEvents(self):
        '''Block until an event appears, then handle it.'''
        if self._isPanning:
            events = pygame.event.get()
        else:
            events = [pygame.event.wait()]

        for event in events:
            try:
                if event.type == pygame.KEYUP:
                    self._keyUpHandlers[event.key]()
                elif event.type == pygame.KEYDOWN:
                    self._keyDownHandlers[event.key]()
            except KeyError:
                pass

    def _printInfo(self):
        '''Print usage instructions and settings to screen.'''
        self._text.print("Escape: quit")
        self._text.print("Up/down: more/fewer octaves")
        self._text.print("PgUp/PgDn: raise/lower persistence by 0.1")
        self._text.print("Home/end: increase/decrease horz. scale")
        self._text.print("Left/right: pan left/right")
        self._text.print("Octaves: " + str(self._perlin.octaves))
        self._text.print("Persistence: " + str(self._perlin.persistence))
        self._text.print("Horz. scale: " + str(self._perlin.scale))
        self._text.print("Pan offset: " + str(self._offset))
        
    def go(self):
        '''Start application using default settings.'''
        self._done = False
        screen = pygame.display.set_mode((self._width, self._height))
        while not self._done:
            self._printInfo()
            self._handleEvents()
            self._pan()
            self._render(screen)
        pygame.display.quit()
        pygame.quit()

    def goWithArgs(self):
        '''Start application using settings from command line.'''
        desc = 'Play around with one-dimensional Perlin noise.'
        parser = argparse.ArgumentParser(description = desc)
        parser.add_argument('--width', '-x',
                            default = DEFAULT_WIDTH,
                            metavar = 'N',
                            help = 'Horizontal viewport size',
                            type = int)
        parser.add_argument('--height', '-y',
                            default = DEFAULT_HEIGHT,
                            metavar = 'N',
                            help = 'Vertical viewport size',
                            type = int)
        parser.add_argument('--pan', '-p',
                            default = DEFAULT_PAN_SPEED,
                            metavar = 'N',
                            help = 'Horizontal pan speed',
                            type = int)
        result = parser.parse_args()
        self._width = result.width
        self._height = result.height
        self._panSpeed = result.pan
        return self.go()

if __name__ == "__main__":
    PerlinToy().goWithArgs()
