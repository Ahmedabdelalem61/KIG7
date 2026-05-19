/** @odoo-module **/
/* eslint-disable no-eval */

import { whenReady } from "@odoo/owl";

whenReady(() => {
    const $ = window.jQuery;
    if (!$) {
        return;
    }

    function getDisplayBox() {
        return document.querySelector(".calculator #display");
    }

    function clickNumbers(displayBox, val, hasEvaluatedRef) {
        if (
            displayBox.innerHTML === "0" ||
            (hasEvaluatedRef.value === true && !isNaN(displayBox.innerHTML))
        ) {
            displayBox.innerHTML = val;
        } else {
            displayBox.innerHTML += val;
        }
        hasEvaluatedRef.value = false;
    }

    function checkLength(num) {
        if (num.toString().length > 16) {
            $("button").prop("disabled", true);
            $(".clear").prop("disabled", false);
            return "Infinity";
        }
        return num;
    }

    function evaluate(displayBox) {
        displayBox.innerHTML = displayBox.innerHTML.replace(",", "");
        displayBox.innerHTML = displayBox.innerHTML.replace("×", "*");
        displayBox.innerHTML = displayBox.innerHTML.replace("÷", "/");
        if (displayBox.innerHTML.indexOf("/0") !== -1) {
            $("#display").css("font-size", "70px");
            $("#display").css("margin-top", "124px");
            $("button").prop("disabled", false);
            $(".clear").attr("disabled", false);
            displayBox.innerHTML = "Division by 0 is undefined!";
            return;
        }
        let result = eval(displayBox.innerHTML);
        if (result.toString().indexOf(".") !== -1) {
            result = result.toFixed(5);
        }
        const checked = checkLength(result);
        displayBox.innerHTML = checked;
    }

    const hasEvaluatedRef = { value: false };

    $(document).on("click", ".calculator #plus_minus", function () {
        const displayBox = getDisplayBox();
        if (!displayBox) {
            return;
        }
        if (eval(displayBox.innerHTML) > 0) {
            displayBox.innerHTML = "-" + displayBox.innerHTML;
        } else {
            displayBox.innerHTML = displayBox.innerHTML.replace("-", "");
        }
    });

    $(document).on("click", ".calculator #clear", function () {
        const displayBox = getDisplayBox();
        if (!displayBox) {
            return;
        }
        displayBox.innerHTML = "0";
        $("button").prop("disabled", false);
        hasEvaluatedRef.value = false;
    });

    const numberButtons = {
        "#one": 1,
        "#two": 2,
        "#three": 3,
        "#four": 4,
        "#five": 5,
        "#six": 6,
        "#seven": 7,
        "#eight": 8,
        "#nine": 9,
        "#zero": 0,
    };

    for (const [selector, value] of Object.entries(numberButtons)) {
        $(document).on("click", `.calculator ${selector}`, function () {
            const displayBox = getDisplayBox();
            if (!displayBox) {
                return;
            }
            checkLength(displayBox.innerHTML);
            clickNumbers(displayBox, value, hasEvaluatedRef);
        });
    }

    $(document).on("click", ".calculator #decimal", function () {
        const displayBox = getDisplayBox();
        if (!displayBox) {
            return;
        }
        if (
            displayBox.innerHTML.indexOf(".") === -1 ||
            (displayBox.innerHTML.indexOf(".") !== -1 &&
                displayBox.innerHTML.indexOf("+") !== -1) ||
            (displayBox.innerHTML.indexOf(".") !== -1 &&
                displayBox.innerHTML.indexOf("-") !== -1) ||
            (displayBox.innerHTML.indexOf(".") !== -1 &&
                displayBox.innerHTML.indexOf("×") !== -1) ||
            (displayBox.innerHTML.indexOf(".") !== -1 &&
                displayBox.innerHTML.indexOf("÷") !== -1)
        ) {
            clickNumbers(displayBox, ".", hasEvaluatedRef);
        }
    });

    $(document).on("click", ".calculator #add", function () {
        const displayBox = getDisplayBox();
        if (!displayBox) {
            return;
        }
        evaluate(displayBox);
        checkLength(displayBox.innerHTML);
        displayBox.innerHTML += "+";
    });

    $(document).on("click", ".calculator #subtract", function () {
        const displayBox = getDisplayBox();
        if (!displayBox) {
            return;
        }
        evaluate(displayBox);
        checkLength(displayBox.innerHTML);
        displayBox.innerHTML += "-";
    });

    $(document).on("click", ".calculator #multiply", function () {
        const displayBox = getDisplayBox();
        if (!displayBox) {
            return;
        }
        evaluate(displayBox);
        checkLength(displayBox.innerHTML);
        displayBox.innerHTML += "×";
    });

    $(document).on("click", ".calculator #divide", function () {
        const displayBox = getDisplayBox();
        if (!displayBox) {
            return;
        }
        evaluate(displayBox);
        checkLength(displayBox.innerHTML);
        displayBox.innerHTML += "÷";
    });

    $(document).on("click", ".calculator #square", function () {
        const displayBox = getDisplayBox();
        if (!displayBox) {
            return;
        }
        let num = Number(displayBox.innerHTML);
        num = num * num;
        checkLength(num);
        displayBox.innerHTML = num;
    });

    $(document).on("click", ".calculator #sqrt", function () {
        const displayBox = getDisplayBox();
        if (!displayBox) {
            return;
        }
        let num = parseFloat(displayBox.innerHTML);
        num = Math.sqrt(num);
        displayBox.innerHTML = Number(num.toFixed(5));
    });

    $(document).on("click", ".calculator #equals", function () {
        const displayBox = getDisplayBox();
        if (!displayBox) {
            return;
        }
        evaluate(displayBox);
        hasEvaluatedRef.value = true;
    });
});
