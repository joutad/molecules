$(document).ready(function() {

	//Elements / index.html
	if (window.location.pathname === '/index.html' || window.location.pathname === '/') {
	
		$.ajax({
			type: "GET",
			url: "/loadElements",
			success: function(response) {
				$('#element-rows').empty();
				$.each(response.elementsList, function(i, el) {
					let elCode = el[1];
					let elName = el[2];
					let elNum = el[0];
					let elColor1 = el[3];
					let elColor2 = el[4];
					let elColor3 = el[5];
					let elRadius = el[6];
					$('#element-rows').append(
						'<tr id="' + i + '">' +
							'<td>' + elCode + '</td>' +
							'<td>' + elName + '</td>' +
							'<td>' + elNum + '</td>\n' +
							'<td>' + elRadius + '</td>\n' +
							'<td>' + elColor1 + '</td>\n' +
							'<td>' + elColor2 + '</td>\n' +
							'<td>' + elColor3 + '</td>\n' +
							'<td>' +
								'<form action="/removeRow">' +
									'<input type="button" class="removeBtn" id="' + i + '" value="Remove">' +
								'</form>' +
							'</td>' +
						'</tr>'
					);
				});
			}
		});

		$(document).on('click', '.removeBtn', function() {
			let row = $(this).closest('tr');
			let code = row.attr('id');
			$.ajax({
				type: "POST",
				url: "/removeElements",
				data: {
					code: code
				},
				success: function(response) {
					row.remove();
				}
			});
		});

		$("#add-btn").click(function() {
			let number = $("#number").val();
			let code = $("#code").val();
			let name = $("#name").val();
			let color1 = $("#color1").val();
			let color2 = $("#color2").val();
			let color3 = $("#color3").val();
			let radius = $("#radius").val();

			$.ajax({
				type: "POST",
				url: "/addElement",
				data: {
					number: number,
					code: code,
					name: name,
					color1: color1,
					color2: color2,
					color3: color3,
					radius: radius
				},
				success: function(response) {

					function checkColorField(color) {
						if (color.length != 6 || /[g-z]|\W/i.test(color)) {
							return false;
						}
						return true;
					}

					let invalid = false;
					for (e in response.elements) {
						if (code === e) {
							console.log(code, "Element already exists in table!");
							invalid = true;
						}
						else if (code.length > 3) {
							console.log(code, "Element cannot be longer than 3 characters!");
							invalid = true;
						}
						else if (code.match(/[^a-zA-Z]/)) {
							console.log(code, "Element cannot include numbers or symbols!");
							invalid = true;
						}
						console.log(code);
					}
					if (!checkColorField(response.color1) || !checkColorField(response.color2) || !checkColorField(response.color3)) {
						console.log("ERROR: at least 1 color field is invalid!", response.color1, response.color2, response.color3);
						invalid = true;
					}
					if (invalid === false) {
						$("#element-rows").append(
						`<tr id="${code}">` + 
							`<td>${code}</td>\n
							<td>${name}</td>\n
							<td>${number}</td>\n
							<td>${radius}</td>\n
							<td>${color1}</td>\n
							<td>${color2}</td>\n
							<td>${color3}</td>\n
							<td>
								<form action="/removeRow">
									<input type="button" class="removeBtn" id="${code}" value="Remove">
								</form>
							</td>` +
						"</tr>");
					}
				}
			});
		});
	
	}
	
	//Upload / upload.html
	if (window.location.pathname === '/upload.html') {
		$("#uploadButton").click(function() {
			let name = $("#moleculeName").val();
			let fileName = $("#uploadFile").val();

			let formData = new FormData($("#uploadSDF")[0]);

			fileName = /C:\\fakepath\\(.*)/i.exec(fileName)[1];

			let invalidFileName = /[\#\%\{\}\<\>\*\?\$\!\'\"\:\@\`\|\=]/i.test(fileName);
			console.log(invalidFileName)

			if (invalidFileName === false) {
				$.ajax({
					type: "POST",
					url: "/uploadSDF",
					data: formData,
					processData: false,
					contentType: false,
					success: function(response) {
						let invalid = false;
						let index = 0;
						console.log(response.molecules);
						if (response.molecules != null) {
							for (e in response.molecules) {
								index = e;
							}
						}
						index++;
						if (response.molecules) {
							for (n in response.molecules) {
								let val = response.molecules[n].toLowerCase();
								if (name.toLowerCase() === val) {
									console.log("Molecule already exists!", name, val);
									invalid = true;
								}
								else if (name.match(/[\.#\%\{\}\<\>\*\?\$\!\'\"\:\@\`\|\=]/i)) {
									console.log("Molecule name cannot contain any of these characters: \.#\%\{\}\<\>\*\?\$\!\'\"\:\@\`\|\=")
									invalid = true;
									break;
								}
							}
			
							if (invalid === false) {
								$("#fileRows").append(
								`<tr id="${name}">` + 
									`<td>${index}</td>\n
									<td>${name}</td>\n
									<td>
										<form action="/removeSDF">
											<input type="button" class="removeBtn" id="${name}" value="Remove">
										</form>
									</td>` +
								"</tr>");
							}		
						}
					}
				});
			}
		})
		$.ajax({
			type: "GET",
			url: "/loadSDF",
			success: function(response) {
				$("#fileRows tr").removeClass();
				$('#fileRows').empty();
				$.each(response.molecules, function(i, molecule) {
					$('#fileRows').append(
						'<tr id="' + molecule[1] + '">' +
							'<td>' + molecule[0] + '</td>' + '<br>' +
							'<td>' + molecule[1] + '</td>' + '<br>' +
							'<td>' +
								'<form action="/removeSDF">' +
									'<input type="button" class="removeBtn" id="' + molecule[1] + '" value="Remove">' +
								'</form>' +
							'</td>' + '<br>' +
						'</tr>'
					);
				});
			}
		});

		$(document).on('click', '.removeBtn', function() {
			let row = $(this).closest('tr');
			let name = row.attr('id');
			$.ajax({
				type: "POST",
				url: "/removeSDF",
				data: {
					name: name,
				},
				success: function(response) {
					row.remove();
				}
			});
		});
	}

	//Molecule / select.html
	if (window.location.pathname === '/select.html') {
		$.ajax({
			type: "GET",
			url: "/loadMolecules",
			success: function(response) {
				$('#moleculeRows').empty();
				$.each(response.molecules, function(i, molecule) {
					$('#moleculeRows').append(
						'<tr id="' + molecule[1] + '">' +
							'<td>' + molecule[0] + '</td>' +
							'<td>' + molecule[1] + '</td>' +
							'<td>Atoms = ' + response["atom_no"][molecule[1]] + '</td>' +
							'<td>Bonds = ' + response["bond_no"][molecule[1]] + '</td>' +
						'</tr>'
					);
				});

				$("#moleculeRows tr").removeClass();
				let sel = response["selected"]
				$("#"+sel).addClass("selected");

				$("#selectedMolecule").attr("value", sel);
			}
		});

		$(document).on('click', '#moleculeRows tr', function() {
			let row = $(this).closest('tr');
			let name = row.attr('id');

			$.ajax({
				type: "POST",
				url: "/selectMolecule",
				data: {
					name: name,
				},
				success: function(response) {
					$("#moleculeRows tr").removeClass();
					row.addClass("selected");
					$("#selectedMolecule").attr("value", name);
				}
			});
		});
	}

	//display molecule
	if (window.location.pathname === '/display.html') {
		$.ajax({
			type: "GET",
			url: "/displayMolecule",
			success: function(response) {
				$('#displayMolecule').empty();
				$("#displayMolecule").append(response["svg"]);
			}
		});
	}

});
