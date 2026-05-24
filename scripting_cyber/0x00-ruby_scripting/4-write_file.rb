require 'json'

def merge_json_files(file1_path, file2_path)
    file1=File.read(file1_path)
    file2=File.read(file2_path)
    file1_data=JSON.parse(file1)
    file2_data=JSON.parse(file2)

    merge = file1_data + file2_data

    File.write(file2_path, JSON.pretty_generate(merge))
    puts "Merged JSON written to  #{file2_data}"
end
