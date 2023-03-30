from __future__ import annotations
from abc import ABC, abstractmethod
from layer_util import *
from referential_array import ArrayR
from layers import *


class LayerStore(ABC):

    def __init__(self) -> None:
        self.layers = ArrayR(100)
        self.layers_by_index = ArrayR(100)

    @abstractmethod
    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store.
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.
        """
        pass

    @abstractmethod
    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def special(self):
        """
        Special mode. Different for each store implementation.
        """
        pass


class SetLayerStore(LayerStore):
    """
    Set layer store. A single layer can be stored at a time (or nothing at all)
    - add: Set the single layer.
    - erase: Remove the single layer. Ignore what is currently selected.
    - special: Invert the colour output.
    """

    def __init__(self) -> None:
        LayerStore.__init__(self)
        self.current_layer = None
        self.current_color = None
        self.special_activate = False
        self.length = 0

    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store.
        Returns true if the LayerStore was actually changed.
        """
        if self.length >= len(self.layers):
            return False
        else:
            self.length += 1
            self.layers[self.length] = layer
            self.current_layer = layer
            return True

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.
        """
        current_layer = self.current_layer
        tem_color = None
        if self.special_activate:
            tem_color = tuple(255 - x for x in self.current_color)
            self.current_color = tem_color
            self.special_activate = False
            return self.current_color
        elif current_layer is rainbow:
            self.current_color = rainbow.apply(start, timestamp, x, y)
            return self.current_color
        elif current_layer is black:
            self.current_color = black.apply(start, timestamp, x, y)
            return self.current_color
        elif current_layer is lighten:
            self.current_color = lighten.apply(start, timestamp, x, y)
            return self.current_color
        elif current_layer is invert:
            self.current_color = invert.apply(start, timestamp, x, y)
            return self.current_color
        elif current_layer is red:
            self.current_color = red.apply(start, timestamp, x, y)
            return self.current_color
        elif current_layer is green:
            self.current_color = green.apply(start, timestamp, x, y)
            return self.current_color
        elif current_layer is blue:
            self.current_color = blue.apply(start, timestamp, x, y)
            return self.current_color
        elif current_layer is sparkle:
            self.current_color = sparkle.apply(start, timestamp, x, y)
            return self.current_color
        elif current_layer is darken:
            self.current_color = darken.apply(start, timestamp, x, y)
            return self.current_color
        elif current_layer is None:
            self.current_color = start
            return self.current_color

    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer
        Returns true if the LayerStore was actually changed.
        """
        if self.current_layer is layer:
            self.length -= 1
            self.current_layer = self.layers[self.length]
            return True
        else:
            self.current_layer = None
            return False

    def special(self):
        """
        Special mode. Different for each store implementation.
        """
        self.special_activate = True


class AdditiveLayerStore(LayerStore):
    """
    Additive layer store. Each added layer applies after all previous ones.
    - add: Add a new layer to be added last.
    - erase: Remove the first layer that was added. Ignore what is currently selected.
    - special: Reverse the order of current layers (first becomes last, etc.)
    """

    def __init__(self) -> None:
        LayerStore.__init__(self)
        self.front = 0
        self.rear = 0
        self.length = 0

    def add(self, layer: Layer):
        if self.length >= len(self.layers):
            return False
        else:
            self.layers[self.rear] = layer
            self.length += 1
            self.rear += 1
            return True

    def erase(self, layer: Layer) -> bool:
        if self.length <= 1:
            return False
        else:
            self.front += 1
            self.length -= 1
            return True

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        current_layer = None
        current_color = start
        final_color = None
        if self.length < 1:
            return start
        else:
            for i in range(self.front, self.rear):
                current_layer = self.layers[i]
                if current_layer is rainbow:
                    final_color = rainbow.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is black:
                    final_color = black.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is lighten:
                    final_color = lighten.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is invert:
                    final_color = invert.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is red:
                    final_color = red.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color
                elif current_layer is green:
                    final_color = green.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is blue:
                    final_color = blue.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is sparkle:
                    final_color = sparkle.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is darken:
                    final_color = darken.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

            return current_color

    def special(self):
        first_layer = self.layers[self.front]
        last_layer = self.layers[self.rear-1]

        self.layers[self.front] = last_layer
        self.layers[self.rear-1] = first_layer


class SequenceLayerStore(LayerStore):
    """
    Sequential layer store. Each layer type is either applied / not applied, and is applied in order of index.
    - add: Ensure this layer type is applied.
    - erase: Ensure this layer type is not applied.
    - special:
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
    """

    def __init__(self) -> None:
        LayerStore.__init__(self)
        self.length = 0
        self.layers_by_index_length = 0

    def _shuffle_right(self, index: int) -> None:
        """ Shuffle items to the right up to a given position. """
        for i in range(self.length, index, -1):
            self.layers[i] = self.layers[i - 1]

    def _shuffle_left(self, index: int):
        for i in range(index, self.length):
            self.layers[i] = self.layers[i + 1]

    def add(self, layer: Layer) -> bool:
        if self.length >= len(self.layers):
            return False
        else:
            position = 0
            index = 0
            for i in range(self.length):
                if self.layers[i].name < layer.name:
                    position += 1
                elif self.layers[i].name == layer.name:
                    return False
                else:
                    break
            for i in range(self.length):
                if self.layers_by_index[i].index < layer.index:
                    index += 1
                else:
                    break
            for i in range(self.length, index, -1):
                self.layers_by_index[i] = self.layers_by_index[i - 1]
            self.layers_by_index[index] = layer
            self._shuffle_right(position)
            self.layers[position] = layer
            self.length += 1
            return True

    def erase(self, layer: Layer) -> bool:
        position = 0
        index = 0
        for i in range(self.length):
            if self.layers_by_index[i].index < layer.index:
                index += 1
            else:
                break
        for i in range(self.length):
            if self.layers[i].name < layer.name:
                position += 1
            else:
                break
        if index < self.length and layer == self.layers_by_index[index]:
            for i in range(index, self.length):
                self.layers_by_index[i] = self.layers_by_index[i + 1]
        if position < self.length and layer == self.layers[position]:
            self.length -= 1
            self._shuffle_left(position)
            return True
        else:
            return False

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        current_layer = None
        current_color = start
        final_color = None
        if self.length < 1:
            return start
        else:
            for i in range(self.length):
                current_layer = self.layers_by_index[i]
                if current_layer is rainbow:
                    final_color = rainbow.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is black:
                    final_color = black.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is lighten:
                    final_color = lighten.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is invert:
                    final_color = invert.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is red:
                    final_color = red.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color
                elif current_layer is green:
                    final_color = green.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is blue:
                    final_color = blue.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is sparkle:
                    final_color = sparkle.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

                elif current_layer is darken:
                    final_color = darken.apply(
                        current_color, timestamp, x, y)
                    current_color = final_color

            return current_color

    def special(self):
        print(self.length)
        if self.length == 2:
            index = 0
        elif self.length % 2 == 0:
            index = int(((self.length) / 2) - 1)
        elif self.length == 2:
            index = 0
        else:
            index = ((self.length) // 2)
        item = self.layers[index]
        position = 0

        for i in range(self.length):
            if self.layers_by_index[i].name != item.name:
                position += 1
            else:
                break
        self.length -= 1
        self._shuffle_left(index)
        for i in range(position, self.length):
            self.layers_by_index[i] = self.layers_by_index[i + 1]


s = SequenceLayerStore()
s.add(invert)
s.add(lighten)
s.add(rainbow)
s.add(black)
for i in range(s.length):
    print(s.layers_by_index[i])
print('')
for i in range(s.length):
    print(s.layers[i])
print(s.get_color(
    (100, 100, 100), 0, 0, 0), (215, 215, 215))
s.special()  # Ordering: Black, Invert, Lighten, Rainbow.
# Remove: Invert
for i in range(s.length):
    print(s.layers_by_index[i])
print('')
for i in range(s.length):
    print(s.layers[i])
print(s.get_color((100, 100, 100), 7, 0, 0), (40, 40, 40))
s.special()  # Ordering: Black, Lighten, Rainbow.
# Remove: Lighten
for i in range(s.length):
    print(s.layers_by_index[i])
print('')
for i in range(s.length):
    print(s.layers[i])
print(s.get_color((100, 100, 100), 7, 0, 0), (0, 0, 0))
s.special()  # Ordering: Black, Rainbow.
# Remove: Black
for i in range(s.length):
    print(s.layers_by_index[i])
print('')
for i in range(s.length):
    print(s.layers[i])
print(s.get_color((100, 100, 100), 7, 0, 0), (91, 214, 104))
