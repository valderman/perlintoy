import math

class Perlin:
    '''Perlin noise generator, using the 2002 algorithm.
       Note that this implementation wraps around at 255.'''
    def __init__(self, octaves=1, persistence=0.5, salt=1):
        # PRNG salt. Should probably be either 1 or a prime; definitely not 0.
        self._salt = salt
        if self._salt == 1:
            self._xs32 = self._unsalted_xs32

        # How many octaves do we use?
        self._octaves = octaves

        # Relative scale of octaves with higher frequency
        self._persistence = persistence

        # More or less arbitrary lookup table
        self._perm = [151,160,137,91,90,15,
           131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
           190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
           88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
           77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
           102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
           135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
           5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
           223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
           129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
           251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
           49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
           138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180,
           151]


    def noise(self, x):
        '''Returns a noise value between -0.5 and 0.5.'''
        y = 0
        maxY = 0
        amp = 1
        freq = 1
        for octave in range(0, self._octaves):
            y += amp*self._octave(x*freq)
            maxY += amp
            freq *= 2
            amp *= self._persistence
        return y/maxY

    def _lerp(self, a, b, t):
        '''Linear interpolation between two values.'''
        return a+t*(b-a)

    def _fade(self, t):
        '''Attenuate value, for smoother curves.'''
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _xs32(self, x):
        '''Simple, fast PRNG for 32 bit integer inputs.'''
        return self._unsalted_xs32(x*self._salt)

    def _unsalted_xs32(self, x):
        '''Unsalted PRNG, for better performance if salt is 1.'''
        x ^= x >> 13
        x ^= x << 17
        x ^= x >> 5
        return x

    def _octave(self, x):
        '''Generate noise for a single octave.'''
        x0 = math.floor(x)
        x1 = x0 + 1
        a = self._grad(self._perm[x0 & 255], x-x0)
        b = self._grad(self._perm[x1 & 255], x-x1)
        return self._lerp(a, b, self._fade(x-x0))

    def _grad(self, xi, x):
        '''One-dimensional gradient vector at the given point.'''
        if self._xs32(xi) & 1:
            return x
        else:
            return -x