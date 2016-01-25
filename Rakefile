require 'rake'
require 'rake/clean'
require 'active_support'

NAME = "Ghostlines"
SRC = "src"
BUNDLE = "#{NAME}.roboFontExt"
STARTUP_FILENAME = "_startup.py"
STARTUP = "#{BUNDLE}/lib/#{STARTUP_FILENAME}"

SOURCE_FILES = FileList[
  "#{SRC}/html/**/*.*",
  "#{SRC}/lib/**/*.*",
  "#{SRC}/Resources/**/*.*"
]

SOURCE_FILES.exclude('*.pyc')
CLEAN.include(FileList['**/*.pyc'])

directory "#{NAME}.roboFontExt"
CLOBBER.include("#{BUNDLE}/**/*")
CLOBBER.exclude("#{BUNDLE}/.env")

SOURCE_FILES.each do |src|
  target = src.pathmap("%{^#{SRC}/,#{BUNDLE}/}p")
  file target => src do
    mkdir_p target.pathmap("%d")
    cp src, target
  end
  task :source => target
end

file "#{BUNDLE}/info.plist" => "#{SRC}/info.yml" do |t|
  require_relative 'tasks/menu_item'
  require 'plist'
  require 'yaml'

  menu_scripts = FileList["#{BUNDLE}/lib/*.py"].exclude(STARTUP)

  data = YAML.load_file t.source
  data['html'] = Dir.exists? "#{BUNDLE}/html"
  data['launchAtStartUp'] = File.exists? STARTUP
  data['mainScript'] = data['launchAtStartUp'] ? STARTUP.pathmap("%f") : ''
  data['timeStamp'] = Time.now.to_f
  data['addToMenu'] = menu_scripts.to_a.collect {|i| MenuItem.new(i).to_hash}
  data.save_plist t.name
end
CLOBBER.include("#{BUNDLE}/info.plist")

task plist: %W[#{BUNDLE} #{BUNDLE}/info.plist]

desc "Compiles an extension from #{SRC}"
task build: [:clean, :clobber, :source, :plist]

desc "Compiles and installs an extension from #{SRC}"
task :install => :build do
  sh "open #{BUNDLE}"
end

desc "Blindly uninstalls an installed #{NAME} extension"
task :uninstall do
  sh "rm -rf ~/Library/Application\\ Support/RoboFont/plugins/#{BUNDLE}"
end

task default: :build
