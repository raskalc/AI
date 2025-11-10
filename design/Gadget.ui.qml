import QtQuick 2.15
import QtQuick.Controls 2.5

Item {
    id: element

    height: 72
    width: 711

    Rectangle {
        id: container

        height: 72
        width: 711

        color: "#ffdddd"
        opacity: 0.80
        radius: 40
    }
    Text {
        id: element_1

        height: 15
        width: 0

        color: "#000000"
        font.family: "Inter"
        font.pixelSize: 12
        font.weight: Font.Normal
        horizontalAlignment: Text.AlignLeft
        text: ""
        verticalAlignment: Text.AlignTop
        wrapMode: Text.WordWrap
    }
    TextArea {
        id: control_2
        x: 0

        y: 0
        width: 711
        background: Rectangle {
            opacity: 0
            color: control_2.enabled ? "transparent" : "#353637"
            border.color: control_2.enabled ? "#21be2b" : "transparent"
        }
        color: "#be226d"
        height: 72

        font.family: "Inter"
        font.pixelSize: 30
        font.weight: Font.Normal
        horizontalAlignment: Text.AlignHCenter
        opacity: 1.00
        placeholderText: "Введите текст..."
        verticalAlignment: Text.AlignVCenter
        wrapMode: Text.WordWrap
        clip: false
    }
}
