// JOK++
import "../application"
import "../basiccontrols"
import "../coincontrols"
import "../dialogs"

BPane {
    id: _base
    property string title: qsTr("Send")
    property var coin // CoinModel

    contentItem: BDialogScrollableLayout {
        columns: 3

        BDialogPromtLabel {
            text: qsTr("Coin:")
        }
        BDialogInputLabel {
            BLayout.columnSpan: parent.columns - 1
            text: _base.coin.fullName
        }

        BDialogSeparator {}

        BDialogPromtLabel {
            text: qsTr("Pay to:")
        }
        BDialogInputTextField {
            text: ""
            onTextEdited: {
                _base.coin.mutableTx.receiver.addressName = text
            }
        }
        BDialogValidLabel {
            status: _base.coin.mutableTx.receiver.validStatus
        }

        BDialogSeparator {}

        BDialogPromtLabel {
            text: qsTr("Available amount:")
        }
        BAmountLabel {
            BLayout.columnSpan: parent.columns - 1
            BLayout.alignment: _applicationStyle.dialogInputAlignment
            orientation: Qt.Horizontal
            amount: _base.coin.txController.availableAmount
        }

        BDialogPromtLabel {
            text: qsTr("Amount:")
        }
        BAmountInput {
            BLayout.alignment: _applicationStyle.dialogInputAlignment
            orientation: Qt.Horizontal
            amount: _base.coin.txController.amount
        }
        BDialogValidLabel {
            status: _base.coin.txController.amount.validStatus
        }

        BDialogSeparator {}

        BDialogPromtLabel {
            text: qsTr("Transaction fee:")
        }
        BAmountLabel {
            BLayout.columnSpan: parent.columns - 1
            BLayout.alignment: _applicationStyle.dialogInputAlignment
            orientation: Qt.Horizontal
            amount: _base.coin.txController.feeAmount
        }

        BDialogPromtLabel {
            text: qsTr("per kilobyte:")
        }
        BAmountInput {
            BLayout.alignment: _applicationStyle.dialogInputAlignment
            orientation: Qt.Horizontal
            amount: _base.coin.txController.kibFeeAmount
            defaultButtonText: qsTr("Recommended")
        }
        BDialogValidLabel {
            status: _base.coin.txController.kibFeeAmount.validStatus
        }

        BDialogPromtLabel {
            text: qsTr("Subtract fee from amount:")
        }
        BDialogInputSwitch {
            BLayout.columnSpan: parent.columns - 1
            checked: _base.coin.txController.feeAmount.subtractFromAmount
            onCheckedChanged: {
                _base.coin.txController.feeAmount.subtractFromAmount = checked
            }
        }

        BDialogSeparator {}

        BDialogPromtLabel {
            text: qsTr("Change:")
        }
        BAmountLabel {
            BLayout.columnSpan: parent.columns - 1
            BLayout.alignment: _applicationStyle.dialogInputAlignment
            orientation: Qt.Horizontal
            amount: _base.coin.txController.changeAmount
        }

        // TODO temporary disabled
        /*BDialogPromtLabel {
            text: qsTr("Send change to new address:")
        }
        BDialogInputSwitch {
            BLayout.columnSpan: parent.columns - 1
            checked: _base.coin.txController.changeAmount.toNewAddress
            onCheckedChanged: {
                _base.coin.txController.changeAmount.toNewAddress = checked
            }
        }

        BDialogSeparator {}

        BDialogPromtLabel {}
        BDialogInputButton {
            BLayout.columnSpan: parent.columns - 1
            text: "Select inputs..."
            onClicked: {
                _inputListDialog.open()
            }
        }*/

        BDialogInputButtonBox {
            BButton {
                BDialogButtonBox.buttonRole: BDialogButtonBox.AcceptRole
                text: qsTr("Prepare...")
                enabled: _base.coin.txController.isValid
            }
            BButton {
                BDialogButtonBox.buttonRole: BDialogButtonBox.ResetRole
                text: BCommon.button.resetRole
            }
            onReset: {
                // TODO
            }
            onAccepted: {
                if (_base.coin.txController.isValid && _base.coin.txController.prepare()) {
                    let dialog = _applicationManager.createDialog(
                                "BTxApproveDialog", {
                                    "type": BTxApproveDialog.Type.Prepare,
                                    "coin": _base.coin
                                })
                    dialog.onAccepted.connect(function () {
                        _base.coin.txController.broadcast() // TODO on error
                    })
                    dialog.open()
                }
            }
        }
    }

    BTxInputListDialog {
        id: _inputListDialog
        inputList: _base.coin.txController.inputList
        onClosed: {
            _base.coin.txController.recalcSources()
        }
    }
}
