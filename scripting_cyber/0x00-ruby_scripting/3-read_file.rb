require 'json'

def count_user_ids(path)
  file = File.read(path)
  data = JSON.parse(file)
  counts = Hash.new(0)

  data.each do |item|
    counts[item["userid"]] +=1
  end
   
  counts.each do |user_id, count|
    puts "#{userid}: #{count}"
  end
end 


