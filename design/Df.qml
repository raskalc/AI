import QtQuick 2.15
import QtQuick.Controls 2.15
ComboBox {
        id: modeSelector
        x: 821.63
        y: 239.31
        width: 151.04

        model: [ "Чат (с памятью)", "Генерация (без)" ] // Упрощенная модель (просто строки)
        currentIndex: 0
    }
