// Get object for queryTable on index.html
var $table = $('#queryTable')
var $button = $('#button')

function getDataFromSQL() {
  var startId = ~~(Math.random() * 100)
  var rows = []

  for (var i = 0; i < 10; i++) {
    rows.push({
        name: 'test' + (startId + i),
        type: 'Q',
        server: '$' + (startId + i),
        description: '$' + (startId + i)
    })
  }
  return rows
}

$(function() {
    $table.bootstrapTable('load', getDataFromSQL())
})
