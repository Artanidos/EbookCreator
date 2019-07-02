#############################################################################
# Copyright (C) 2019 Olaf Japp
#
# self file is part of EbookCreator.
#
#  EbookCreator is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  EbookCreator is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with EbookCreator.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from PyQt5.QtWidgets import QWidget, QSlider, QSpinBox, QLabel, QGridLayout, QLineEdit
from PyQt5.QtGui import QColor, QPainter, QImage
from PyQt5.QtCore import pyqtSignal, QSize, Qt
from colorpicker import ColorPicker
from colorrect import ColorRect


class ColorEditor(QWidget):
    colorChanged = pyqtSignal(object)

    def __init__(self, label, parent=None):
        super(ColorEditor, self).__init__(parent)
        layout = QGridLayout()
        self.color = QLineEdit()
        self.colorPicker = ColorPicker()
        self.colorPicker.setVisible(False)
        self.hueSlider = QSlider()
        self.hueSlider.setVisible(False)
        self.hueSlider.setMinimum(0)
        self.hueSlider.setMaximum(100.0)
        self.hueSlider.setOrientation(Qt.Vertical)
        self.hueSlider.setMaximumHeight(100.0)
        self.rect = ColorRect()
        self.hue = QSpinBox()
        self.saturation = QSpinBox()
        self.lightness = QSpinBox()
        self.labelHue = QLabel("H")
        self.labelSaturation = QLabel("S")
        self.labelLightness = QLabel("L")
        self.red = QSpinBox()
        self.green = QSpinBox()
        self.blue = QSpinBox()
        self.labelRed = QLabel("R")
        self.labelGreen = QLabel("G")
        self.labelBlue = QLabel("B")
        self.hue.setVisible(False)
        self.saturation.setVisible(False)
        self.lightness.setVisible(False)
        self.red.setVisible(False)
        self.green.setVisible(False)
        self.blue.setVisible(False)
        self.labelHue.setVisible(False)
        self.labelSaturation.setVisible(False)
        self.labelLightness.setVisible(False)
        self.labelRed.setVisible(False)
        self.labelGreen.setVisible(False)
        self.labelBlue.setVisible(False)
        self.red.setMinimum(0)
        self.red.setMaximum(255)
        self.green.setMinimum(0)
        self.green.setMaximum(255)
        self.blue.setMinimum(0)
        self.blue.setMaximum(255)
        self.hue.setMinimum(0)
        self.hue.setMaximum(100.0)
        self.saturation.setMinimum(0)
        self.saturation.setMaximum(100.0)
        self.lightness.setMinimum(0)
        self.lightness.setMaximum(100.0)
        self.labelHue.setFixedWidth(15)
        self.labelSaturation.setFixedWidth(15)
        self.labelLightness.setFixedWidth(15)
        self.labelRed.setFixedWidth(15)
        self.labelGreen.setFixedWidth(15)
        self.labelBlue.setFixedWidth(15)
        l = QLabel(label)
        l.setMinimumWidth(100.0)

        layout.addWidget(l, 0, 0)
        layout.addWidget(self.rect, 0, 1)
        layout.addWidget(self.color, 0, 2, 1, 3)
        layout.addWidget(self.colorPicker, 1, 0, 3, 2)
        layout.addWidget(self.hueSlider, 1, 2, 3, 1)
        layout.addWidget(self.labelHue, 1, 3)
        layout.addWidget(self.hue, 1, 4)
        layout.addWidget(self.labelSaturation, 2, 3)
        layout.addWidget(self.saturation, 2, 4)
        layout.addWidget(self.labelLightness, 3, 3)
        layout.addWidget(self.lightness, 3, 4)
        layout.addWidget(self.labelRed, 1, 5)
        layout.addWidget(self.red, 1, 6)
        layout.addWidget(self.labelGreen, 2, 5)
        layout.addWidget(self.green, 2, 6)
        layout.addWidget(self.labelBlue, 3, 5)
        layout.addWidget(self.blue, 3, 6)
        self.setLayout(layout)
        self.connectControls()

    def color(self):
        return QColor(self.color.text())

    def setColor(self, color):
        self.setColorParts(color)

    def disconnectControls(self):
        self.color.editingFinished.disconnect()
        self.hueSlider.valueChanged.disconnect()
        self.hueSlider.sliderReleased.disconnect()
        self.colorPicker.colorChanged.disconnect()
        self.colorPicker.colorPicked.disconnect()
        self.rect.mouseClicked.disconnect()
        self.hue.valueChanged.disconnect()
        self.saturation.valueChanged.disconnect()
        self.lightness.valueChanged.disconnect()
        self.red.valueChanged.disconnect()
        self.green.valueChanged.disconnect()
        self.blue.valueChanged.disconnect()

    def connectControls(self):
        self.color.editingFinished.connect(self.colorTextChanged)
        self.hueSlider.valueChanged.connect(self.hueChanged)
        self.hueSlider.sliderReleased.connect(self.huePicked)
        self.colorPicker.colorChanged.connect(self.colorPickerChanged)
        self.colorPicker.colorPicked.connect(self.colorPicked)
        self.rect.mouseClicked.connect(self.rectClicked)
        self.hue.valueChanged.connect(self.hueValueChanged)
        self.saturation.valueChanged.connect(self.saturationValueChanged)
        self.lightness.valueChanged.connect(self.lightnessValueChanged)
        self.red.valueChanged.connect(self.redValueChanged)
        self.green.valueChanged.connect(self.greenValueChanged)
        self.blue.valueChanged.connect(self.blueValueChanged)

    def rectClicked(self):
        self.setExpanded(not self.colorPicker.isVisible())

    def setExpanded(self, value):
        self.colorPicker.setVisible(value)
        self.hueSlider.setVisible(value)
        self.labelHue.setVisible(value)
        self.labelSaturation.setVisible(value)
        self.labelLightness.setVisible(value)
        self.hue.setVisible(value)
        self.saturation.setVisible(value)
        self.lightness.setVisible(value)
        self.labelRed.setVisible(value)
        self.labelGreen.setVisible(value)
        self.labelBlue.setVisible(value)
        self.red.setVisible(value)
        self.green.setVisible(value)
        self.blue.setVisible(value)

    def isExpanded(self):
        return self.colorPicker.isVisible()

    def setColorParts(self, value):
        self.disconnectControls()
        self.hue.setValue(round(value.hslHueF() * 100.0))
        self.hueSlider.setValue(round(value.hslHueF() * 100.0))
        self.colorPicker.setHue(value.hslHueF())
        self.saturation.setValue(round(value.hslSaturationF() * 100.0))
        self.lightness.setValue(round(value.lightnessF() * 100.0))
        self.red.setValue(value.red())
        self.green.setValue(value.green())
        self.blue.setValue(value.blue())
        self.color.setText(value.name())
        self.rect.setColor(value)
        self.connectControls()

    def colorTextChanged(self):
        color = QColor(self.color.text())
        self.setColorParts(color)
        self.colorChanged.emit(color)

    def colorPicked(self, value):
        self.setColorParts(value)
        self.colorChanged.emit(value)

    def colorPickerChanged(self, value):
        self.setColorParts(value)

    def hueChanged(self, value):
        self.colorPicker.setHue(value / 100.0)
        color = QColor.fromHslF(value / 100.0, self.saturation.value() / 100.0, self.lightness.value() / 100.0, 1.0)
        self.setColorParts(color)

    def hueValueChanged(self, value):
        self.hueSlider.setValue(value)
        color = QColor.fromHslF(value / 100.0, self.saturation.value() / 100.0, self.lightness.value() / 100.0, 1.0)
        self.setColorParts(color)
        self.colorChanged.emit(color)

    def huePicked(self):
        value = self.hueSlider.value()
        self.colorPicker.setHue(value / 100.0)
        color = QColor.fromHslF(value / 100.0, self.saturation.value() / 100.0, self.lightness.value() / 100.0, 1.0)
        self.setColorParts(color)
        self.colorChanged.emit(color)

    def saturationValueChanged(self, value):
        color = QColor.fromHslF(self.hue.value() / 100.0, value / 100.0, self.lightness.value() / 100.0, 1.0)
        self.setColorParts(color)
        self.colorChanged.emit(color)

    def lightnessValueChanged(self, value):
        color = QColor.fromHslF(self.hue.value() / 100.0, self.saturation.value() / 100.0, value / 100.0, 1.0)
        self.setColorParts(color)
        self.colorChanged.emit(color)

    def redValueChanged(self, value):
        color = QColor.fromRgb(value, self.green.value(), self.blue.value())
        self.setColorParts(color)
        self.colorChanged.emit(color)

    def greenValueChanged(self, value):
        color = QColor.fromRgb(self.red.value(), value, self.blue.value())
        self.setColorParts(color)
        self.colorChanged.emit(color)

    def blueValueChanged(self, value):
        color = QColor.fromRgb(self.red.value(), self.green.value(), value)
        self.setColorParts(color)
        self.colorChanged.emit(color)
