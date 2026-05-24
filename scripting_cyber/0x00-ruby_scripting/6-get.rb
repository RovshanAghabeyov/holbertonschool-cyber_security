require 'net/http'
require 'json'
require 'uri'

def get_request(url)
  uri = URI(url)
  response = Net::HTTP.get_response(uri)

  puts "Response status: #{response.code} #{response.message}"
  puts "Response body:"

  json_body = JSON.pretty_generate(JSON.parse(response.body))
  puts json_body
end
