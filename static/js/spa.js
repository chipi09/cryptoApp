xhr = new XMLHttpRequest()

function llamadaMovimientos() {
    xhr.open("GET", "http://localhost:5000/api/v1/movimientos", true)
    xhr.send()

    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            let response = xhr.responseText
            let jsonResponse = JSON.parse(response)
            if (xhr.status == "200") {
                $("#table-body").empty()
                for (let i = 0 ; i < jsonResponse.data.length ; i++){
                    $("#table-body").append("<tr id=fila_" + jsonResponse.data[i][0] + ">")
                    for (let j = 1 ; j < jsonResponse.data[i].length ; j++){
                        $("#fila_" + jsonResponse.data[i][0]).append("<td>" + jsonResponse.data[i][j] + "</td>")
                    }
                }
                llamadaStatus()
            }
        }
    }
}

function llamadaMovimiento() {
    var d = new Date();
    fecha = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2)
    hora = d.getHours() + ":" + (d.getMinutes() < 10 ? ('0' + d.getMinutes()) : d.getMinutes()) + ":" + (d.getSeconds() < 10 ? '0' + d.getSeconds() : d.getSeconds()) + "." + d.getMilliseconds()
    from_moneda = $("#select-from-moneda").val()
    from_cantidad =  $("#input-from-cantidad").val()
    to_moneda = $("#select-to-moneda").val()
    to_cantidad = $("#input-to-cantidad").val()

    if (from_moneda != "EUR") {
        xhr.open("GET", "http://localhost:5000/api/v1/comprobar-saldo/" + from_moneda, true)
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
        xhr.send()

        xhr.onreadystatechange = function() {
            if (xhr.readyState == XMLHttpRequest.DONE) {
                let response = xhr.responseText
                let jsonResponse = JSON.parse(response)
                if (xrh.status == "200") {
                    alert("ERROR 200: " + jsonResponse.mensaje)
                    return
                }
                if (xrh.status == "400") {
                    alert("ERROR 400: " + jsonResponse.mensaje)
                    return
                }
            }
        }
    }

    let json = {
        fecha: fecha,
        hora: hora,
        from_moneda: from_moneda,
        from_cantidad: from_cantidad,
        to_moneda: to_moneda,
        to_cantidad: to_cantidad
    }

    xhr.open("POST", "http://localhost:5000/api/v1/movimiento", true)
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    xhr.send(JSON.stringify(json))

    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            let response = xhr.responseText
            let jsonResponse = JSON.parse(response)

            if (xhr.status == "400")
                alert("ERROR 400: " + jsonResponse.mensaje)
            if (xhr.status == "200")
                alert("ERROR 200: " + jsonResponse.mensaje)
            if (xhr.status == "201")
                llamadaMovimientos()
        }
    }
}

function llamadaStatus() {
    xhr.open("GET", "http://localhost:5000/api/v1/status", true)
    xhr.send()

    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            let response = xhr.responseText
            let jsonResponse = JSON.parse(response)
            if (xhr.status == "200") {
                $("#span-invertido").text(jsonResponse.data.invertido)
                $("#span-valor").text(jsonResponse.data.valor_actual)
                var resultado = Math.round((jsonResponse.data.valor_actual - jsonResponse.data.invertido) * 100) / 100
                $("#span-resultado").text(resultado)
                if (resultado > 0)
                    $("#span-resultado").removeClass("negativo")
                else
                    $("#span-resultado").addClass("negativo")
            }
            if (xhr.status == "400") {
                alert("ERROR 400: " + jsonResponse.mensaje)
            }
            llamadaActualizarApi()
        }
    }
    
}
function llamadaConvertirMoneda() {
    from_moneda = $("#select-from-moneda").val()
    to_moneda = $("#select-to-moneda").val()
    from_cantidad =  $("#input-from-cantidad").val()

    let json = {
        from_moneda: from_moneda,
        to_moneda: to_moneda,
        from_cantidad: from_cantidad
    } 

    xhr.open("POST", "http://localhost:5000/api/v1/convertir-moneda", true)
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    xhr.send(JSON.stringify(json))

    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            let response = xhr.responseText
            let jsonResponse = JSON.parse(response)
            if (xhr.status == "200") {
                $("#input-to-cantidad").val(jsonResponse.to_cantidad)
                precio_unitario = jsonResponse.to_cantidad/from_cantidad
                $("#input-precio-unitario").val(precio_unitario)
                
                from_moneda = $("#select-from-moneda").val()
                to_moneda = $("#select-to-moneda").val()
                if (from_moneda != to_moneda)
                    $("#btn-llamar-mov").prop("disabled", false);
            }
            if (xhr.status == "400") {
                alert("ERROR 400: " + jsonResponse.mensaje)
            }
            llamadaActualizarApi()
        }
    }
}

function llamadaActualizarApi() {
    xhr.open("GET", "http://localhost:5000/api/v1/actualizar-api", true)
    xhr.send()
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            let response = xhr.responseText
            let jsonResponse = JSON.parse(response)
            if (xhr.status == "200") {
                $("#span-limite-llamadas-dia").text(jsonResponse.limite_diario)
                $("#span-limite-llamadas-mes").text(jsonResponse.limite_mensual)
                $("#span-llamadas-dia").text(jsonResponse.usos_dia_actual)
                $("#span-llamadas-mes").text(jsonResponse.usos_mes_actual)
            }
        }
    }
}


function activarFormulario() {
    if ($("#btn-cancelar").is(":disabled") && $("#select-to-moneda").is(":disabled") && $("#select-from-moneda").is(":disabled") && $("#input-from-cantidad").is(":disabled"))  {
        $("#btn-cancelar").prop("disabled", false);
        $("#select-from-moneda").prop("disabled", false);
        $("#select-to-moneda").prop("disabled", false);
        $("#input-from-cantidad").prop("disabled", false);
    }
    else {
        $("#btn-cancelar").prop("disabled", true);
        $("#select-from-moneda").prop("disabled", true);
        $("#select-to-moneda").prop("disabled", true);
        $("#input-from-cantidad").prop("disabled", true);
    }
    $("#input-from-cantidad").val("")
    $("#input-to-cantidad").val("")
    $("#input-precio-unitario").val("")
    $("#btn-llamar-mov").prop("disabled", true);
}

function cancelarMovimiento() {
    $("#input-from-cantidad").val("")
    $("#input-to-cantidad").val("")
    $("#input-precio-unitario").val("")
    $("#btn-llamar-mov").prop("disabled", true);
}


$(document).ready( function () {
    llamadaMovimientos()

    $("#select-from-moneda, #select-to-moneda").change(function () {
        $("#btn-llamar-mov").prop("disabled", true);
        $("#input-from-cantidad").val("")
        $("#input-to-cantidad").val("")
        $("#input-precio-unitario").val("")
        $("#btn-convertir-moneda").prop("disabled", true)
    })

    $("#formulario :input").on("input", function() {
        $("#btn-llamar-mov").prop("disabled", true);
        if ($("#input-from-cantidad").val() == "")
            $("#btn-convertir-moneda").prop("disabled", true)
        else
            $("#btn-convertir-moneda").prop("disabled", false)
    })
})
