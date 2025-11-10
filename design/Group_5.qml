import QtQuick 2.15 // <-- Added version number (2.15 is standard for Qt 5.15)
import QtQuick.Shapes 1.15 // <-- Added version number (1.15 is standard for this module)
import "." as Untitled
import QtQuick.Controls 2.5

ApplicationWindow {
  visible: true

    title: "My QML App"

    height: 796
    width: 1314

    Rectangle {
        id: rectangle_1

        height: 796.16
        width: 1022.72

        color: "#edc0c0"
    }
    Rectangle {
        id: rectangle_5

        x: 1020.90

        height: 796.16
        width: 293.44

        color: "#edc0c0"
    }
    Text {
        id: pupuAI_

        x: 118
        y: 16

        height: 36
        width: 613

        color: "#a94f4f"
        font.family: "Century Gothic"
        font.pixelSize: 32
        font.weight: Font.Normal
        horizontalAlignment: Text.AlignLeft
        text: "PupuAI - Твоя розовая помощница "
        verticalAlignment: Text.AlignTop
    }
    Rectangle {
        id: rectangle_2

        x: 37.76
        y: 63.24

        height: 691.52
        width: 742.93

        color: "#efa3a3"
        radius: 60
    }
    Text {
        id: generate_

        x: 92
        y: 261

        height: 11
        width: 114

        color: "#ffffff"
        font.family: "Inter"
        font.pixelSize: 15
        font.weight: Font.Normal
        horizontalAlignment: Text.AlignLeft
        text: "Generate..."
        verticalAlignment: Text.AlignTop
    }
    Untitled.Gadget {
        id: element

        x: 54
        y: 655
    }
    Rectangle {
        id: rectangle_3

        x: 63.69
        y: 107.82

        height: 46.86
        width: 230.66

        color: "#d37070"
        radius: 40
    }
    Rectangle {
        id: rectangle_4

        x: 63.69
        y: 182.89

        height: 46.86
        width: 347.12

        color: "#d37070"
        radius: 40
    }
    Rectangle {
        id: rectangle_6

        x: 1052.29
        y: 52.32

        height: 46.86
        width: 230.66

        color: "#d37070"
        radius: 40
    }
    Rectangle {
        id: rectangle_8

        x: 1052.29
        y: 193.35

        height: 46.86
        width: 230.66

        color: "#d37070"
        radius: 40
    }
    Rectangle {
        id: rectangle_7

        x: 1052.29
        y: 121.93

        height: 46.86
        width: 230.66

        color: "#d37070"
        radius: 40
    }
    Text {
        id: element_1

        x: 82.80
        y: 121.93

        height: 19.56
        width: 198.81

        color: "#ffffff"
        font.family: "Century Gothic"
        font.pixelSize: 15
        font.weight: Font.Normal
        horizontalAlignment: Text.AlignLeft
        text: "Привет, задавай вопрос!"
        verticalAlignment: Text.AlignTop
    }
    Text {
        id: element_2

        x: 82.80
        y: 196.99

        height: 19.56
        width: 322.10

        color: "#ffffff"
        font.family: "Century Gothic"
        font.pixelSize: 15
        font.weight: Font.Normal
        horizontalAlignment: Text.AlignLeft
        text: "Привет, мне нужно сгенерировать стих)"
        verticalAlignment: Text.AlignTop
    }
    Text {
        id: element_3

        x: 1077.31
        y: 65.06

        height: 19.56
        width: 181.07

        color: "#ffffff"
        font.family: "Century Gothic"
        font.pixelSize: 15
        font.weight: Font.Normal
        horizontalAlignment: Text.AlignLeft
        text: "Привет, мне нужно с..."
        verticalAlignment: Text.AlignTop
    }
    Image {
        id: ellipse_1

        x: 71.88
        y: 257.95

        source: "assets/ellipse_1.png"
    }
    Button {
        id: group_3

        x: 821.63
        y: 63.24

        height: 44.58
        width: 151.04

        Shape {
            id: rectangle_9

            height: 44.58
            width: 151.04

            ShapePath {
                id: rectangle_9_ShapePath0

                fillColor: "#c96a6a"
                fillRule: ShapePath.WindingFill
                strokeColor: "transparent"
                strokeWidth: 1

                PathSvg {
                    id: rectangle_9_ShapePath0_PathSvg0

                    path: "M 0 0 L 151.04202270507812 0 L 151.04202270507812 44.58469009399414 L 0 44.58469009399414 L 0 0 Z"
                }
            }

            Text {
                id: element_4

                x: 19
                y: 11

                height: 22
                width: 113

                color: "#ffffff"
                font.family: "Century Gothic"
                font.pixelSize: 20
                font.weight: Font.Normal
                horizontalAlignment: Text.AlignLeft
                text: "Сохранить"
                verticalAlignment: Text.AlignTop
            }
        }

        onClicked: {
            console.debug("save clicked")
        }
    }
    Button {
        id: group_2

        x: 828.91
        y: 682.42
         hoverEnabled: false
        height: 44.58

        width: 151.04
        onClicked: {
            console.debug("generate clicked")
        }

        background:
            Rectangle {
                id: rectangle_10

                height: 44.58
                width: 151.04

                color: "#c96a6a"
                radius: 40
            }

        Text {
            id: element_5

            x: 15
            y: 11

            height: 22.29
            width: 140.58

            color: "#ffffff"
            font.family: "Century Gothic"
            font.pixelSize: 16
            font.weight: Font.Normal
            horizontalAlignment: Text.AlignLeft
            text: "Сгенерировать"
            verticalAlignment: Text.AlignTop
        }
    }
    Item {
        id: group_4

        x: 821.63
        y: 121.93

        height: 44.58
        width: 151.04

        Rectangle {
            id: rectangle_11

            height: 44.58
            width: 151.04

            color: "#c96a6a"
            radius: 40
        }
        Text {
            id: element_6

            x: 35.37
            y: 11.07

            height: 22
            width: 91

            color: "#ffffff"
            font.family: "Century Gothic"
            font.pixelSize: 20
            font.weight: Font.Normal
            horizontalAlignment: Text.AlignLeft
            text: "История"
            verticalAlignment: Text.AlignTop
        }
    }
    Text {
        id: element_7

        x: 1096
        y: 16

        height: 27.75
        width: 161.51

        color: "#a94f4f"
        font.family: "Century Gothic"
        font.pixelSize: 20
        font.weight: Font.Normal
        horizontalAlignment: Text.AlignLeft
        text: "История чатов"
        verticalAlignment: Text.AlignTop
    }
}

/*##^##
Designer {
    D{i:0;formeditorZoom:0.75}D{i:1}D{i:2}D{i:3}D{i:4}D{i:5}D{i:6}D{i:7}D{i:8}D{i:9}D{i:10}
D{i:11}D{i:12}D{i:13}D{i:14}D{i:15}D{i:18}D{i:20}D{i:17}D{i:16}D{i:23}D{i:21}D{i:25}
D{i:26}D{i:24}D{i:27}
}
##^##*/

