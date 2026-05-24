require 'digest'

def crack_password(hashed_password, dictionary_file)
  unless File.exist?(dictionary_file)
    puts "Dictionary file not found."
    return
  end

  File.foreach(dictionary_file) do |word|
    word = word.strip
    hash = Digest::SHA256.hexdigest(word)

    if hash == hashed_password
      puts "Password found: #{word}"
      return
    end
  end

  puts "Password not found in dictionary."
end

# CLI handling
if ARGV.length != 2
  puts "Usage: 10-password_cracked.rb HASHED_PASSWORD DICTIONARY_FILE"
  exit
end

hashed_password = ARGV[0]
dictionary_file = ARGV[1]

crack_password(hashed_password, dictionary_file)
