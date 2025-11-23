import QtQuick 2.15
import QtQuick.Shapes 1.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.1

Window{
    visible: true
    title: "PupuAI - Твоя розовая помощница"
    height: 796
    width: 1314

    Rectangle {
        id: mainBackground
        height: 796.16
        width: parent.width
        color: "#edc0c0"
    }

    Text {
        id: pupuAI_
        x: 118
        y: 16
        color: "#a94f4f"
        font.family: "Century Gothic"
        font.pixelSize: 32
        font.weight: Font.Normal
        text: "PupuAI - Твоя розовая помощница"
    }

    // --- Область чата/вывода (без изменений) ---
    Rectangle {
        id: chatArea
        x: 37.76
        y: 63.24
        height: 610.52
        width: 742.93
        color: "#efa3a3"
        radius: 60
        clip: true

        Flickable {
            id: chatFlickable
            anchors.fill: parent
            anchors.margins: 30
            clip: true
            flickableDirection: Flickable.VerticalFlick
            ScrollBar.vertical: ScrollBar {}
            ScrollBar.horizontal: null

            TextArea.flickable: TextArea {
                id: chatOutput
                font.family: "Century Gothic"
                font.pixelSize: 16
                color: "#a94f4f"
                readOnly: true
                wrapMode: TextArea.WordWrap

                Component.onCompleted: {
                    text = "Привет! Я PupuAI, ваша розовая помощница.\n"
                }
            }
            function scrollToBottom() {
                contentY = contentHeight - height
            }
        }
    }

    // --- Поле ввода запроса (без изменений) ---
    Rectangle {
        id: inputBackground
        x: 37.76
        y: 682.42
        height: 60
        width: 742.93
        color: "#d37070"
        radius: 30

        TextField {
            id: promptInput
            anchors.fill: parent
            anchors.margins: 10
            placeholderText: "Введите ваш запрос здесь..."
            font.family: "Century Gothic"
            font.pixelSize: 18
            color: "white"
            background: Rectangle { color: "transparent" }
            enabled: !aiWorker.isWorking
            onAccepted: group_2.clicked()
        }
    }

    // -------------------------------------------------------------------
    // --- ИЗМЕНЕНО: Колонка истории (правая панель) ---
    // -------------------------------------------------------------------
    Rectangle {
        id: historyPanel
        x: 1020.90
        height: 796.16
        width: 293.44
        color: "#edc0c0"
    }
    Text {
        id: historyTitle
        x: 1096
        y: 16
        color: "#a94f4f"
        font.family: "Century Gothic"
        font.pixelSize: 20
        font.weight: Font.Normal
        text: "История чатов"
    }

    // --- ИЗМЕНЕНО: Динамический список для истории чатов ---
    Flickable {
        id: historyFlickable
        x: 1035.9 // (1020.90 + 15)
        y: 55 // (16 + 20 + 19 (отступ))
        width: 263.44 // (293.44 - 30 (отступы))
        height: 721 // (796 - 55 - 20 (отступы))

        clip: true
        flickableDirection: Flickable.VerticalFlick
        ScrollBar.vertical: ScrollBar {}

        ListView {
            id: historyListView
            anchors.fill: parent
            spacing: 10

            // Модель будет установлена из Python (aiWorker.historyListChanged)
            model: []

            // Делегат (как выглядит каждый элемент списка)
            delegate: ItemDelegate {
                width: parent.width
                height: 50

                background: Rectangle {
                    color: "#d37070"
                    radius: 20
                    border.color: held ? "#a94f4f" : "transparent"
                    border.width: 2
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 15
                    anchors.rightMargin: 10
                    spacing: 10

                    // Имя файла (modelData - это элемент из списка model)
                    Text {
                        Layout.fillWidth: true
                        text: modelData
                        color: "white"
                        font.family: "Century Gothic"
                        elide: Text.ElideRight // Обрезать, если не влезает
                    }

                    // Кнопка удаления "X"
                    Button {
                        text: "X"
                        font.pixelSize: 12
                        font.bold: true
                        Layout.preferredWidth: 30
                        Layout.preferredHeight: 30
                        background: Rectangle {
                            color: "#a94f4f"
                            radius: 15
                        }
                        onClicked: {
                            // Остановить всплытие клика,
                            // чтобы не загрузился чат
                            mouse.accepted = true
                            aiWorker.deleteChat(modelData)
                        }
                    }
                }

                // При клике на сам элемент - загружаем чат
                onClicked: {
                    aiWorker.loadChat(modelData)
                }
            }
        }
    }


    // --- Кнопка "Сгенерировать" (group_2) ---
    Button {
        id: group_2
        x: 828.91
        y: 692.42
        height: 44.58
        width: 151.04
        enabled: !aiWorker.isWorking && promptInput.text.trim().length > 0

        onClicked: {
            var currentPrompt = promptInput.text
            promptInput.clear()

            // ИЗМЕНЕНО: Берем режим из ComboBox
            aiWorker.startGeneration(
                currentPrompt,
                modeSelector.currentValue, // <--- ИЗМЕНЕНИЕ ЗДЕСЬ
                400
            );
        }

        background: Rectangle {
            id: rectangle_10
            height: 44.58
            width: 151.04
            color: group_2.enabled ? "#c96a6a" : "#999999"
            radius: 40
        }
        Text {
            id: element_5
            anchors.centerIn: parent
            color: "#ffffff"
            font.family: "Century Gothic"
            font.pixelSize: 16
            text: aiWorker.isWorking ? "Обработка..." : "Сгенерировать"
        }
    }

    // --- Индикатор загрузки (без изменений) ---
    BusyIndicator {
        id: busyIndicator
        anchors.centerIn: group_2
        running: aiWorker.isWorking
        visible: aiWorker.isWorking
        height: 44.58
        width: 44.58
    }

    // --- ИЗМЕНЕНО: Кнопка "Сохранить чат" ---
    Button {
        id: group_3
        x: 821.63
        y: 63.24
        height: 44.58
        width: 151.04
        background: Rectangle { color: "#c96a6a"; radius: 20; border.color: "#993333"; border.width: 2; }
        Text {
            anchors.centerIn: parent; color: "#ffffff"; font.family: "Century Gothic"; font.pixelSize: 20;
            text: "Сохранить чат" // ИЗМЕНЕН ТЕКСТ
        }
        // ИЗМЕНЕНО: Вызываем слот сохранения
        onClicked: {
            aiWorker.saveCurrentChat()
        }
    }

    // --- ИЗМЕНЕНО: Кнопка "Обновить" (список истории) ---
    Button {
        id: group_4
        x: 821.63
        y: 121.93
        height: 44.58
        width: 151.04
        background: Rectangle { color: "#c96a6a"; radius: 20; border.color: "#993333"; border.width: 2; }
        Text {
            anchors.centerIn: parent; color: "#ffffff"; font.family: "Century Gothic"; font.pixelSize: 20;
            text: "Обновить" // ИЗМЕНЕН ТЕКСТ
        }
        // ИЗМЕНЕНО: Вызываем слот обновления
        onClicked: {
            aiWorker.refreshChatList()
        }
    }

    // --- Кнопка "Новый чат" (без изменений) ---
    Button {
        id: newChatButton
        x: 821.63
        y: 180.62
        height: 44.58
        width: 151.04
        background: Rectangle { color: "#c96a6a"; radius: 20; border.color: "#993333"; border.width: 2; }
        Text {
            anchors.centerIn: parent; color: "#ffffff"; font.family: "Century Gothic"; font.pixelSize: 20; text: "Новый чат"
        }
        onClicked: {
            aiWorker.clearChatHistory()
        }
    }



ComboBox {
        id: modeSelector
        x: 821.63
        y: 239.31
        width: 151.04
        height: 44.58
        model: [ "chat", "gen" ] // Упрощенная модель (просто строки)
        currentIndex: 0
        font.family: "Century Gothic"
        font.pixelSize: 20
        background: Rectangle {
            color: "#c96a6a"
            radius: 20
            border.color: "#993333"
            border.width: 2
        }


    }
    // --- ИЗМЕНЕНИЕ: Подписка на сигналы (Connections) ---
    Connections {
        target: aiWorker

        // (Этот блок без изменений, но важен)
        function onAiResponseReady(message) {
            var atBottom = (chatFlickable.contentY >= chatFlickable.contentHeight - chatFlickable.height - 20)
            chatOutput.append(message)
            chatOutput.append("")
            if (atBottom) {
                Qt.callLater(chatFlickable.scrollToBottom)
            }
        }

        // (Этот блок без изменений, но важен)
        function onClearChatDisplay() {
            chatOutput.clear()
            Qt.callLater(chatFlickable.scrollToBottom)
        }

        // --- ДОБАВЛЕНО: Подписка на обновление списка истории ---
        function onHistoryListChanged(files) {
            historyListView.model = files
        }
    }
}

