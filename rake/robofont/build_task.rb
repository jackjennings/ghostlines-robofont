require 'rake'
require 'rake/clean'
require 'rake/tasklib'
require 'active_support'

module Rake
  module Robofont
    class BuildTask < TaskLib

      def initialize extension_name
        src_filepath = "src"
        bundle_filename = "#{extension_name}.roboFontExt"
        startup_filename = "_startup.py"
        startup_filepath = "#{bundle_filename}/lib/#{startup_filename}"

        source_files = FileList[
          "#{src_filepath}/html/**/*.*",
          "#{src_filepath}/lib/**/*.*",
          "#{src_filepath}/Resources/**/*.*"
        ]

        source_files.exclude('*.pyc')
        CLEAN.include(FileList['**/*.pyc'])

        directory "#{extension_name}.roboFontExt"
        CLOBBER.include("#{bundle_filename}/**/*")
        CLOBBER.exclude("#{bundle_filename}/.env")

        source_files.each do |src|
          target = src.pathmap("%{^#{src_filepath}/,#{bundle_filename}/}p")
          file target => src do
            mkdir_p target.pathmap("%d")
            cp src, target
          end
          task :source => target
        end

        file "#{bundle_filename}/info.plist" => "#{src_filepath}/info.yml" do |t|
          require_relative './menu_item'
          require 'plist'
          require 'yaml'

          menu_scripts = FileList["#{bundle_filename}/lib/*.py"].exclude(startup_filepath)

          data = YAML.load_file t.source
          data['html'] = Dir.exists? "#{bundle_filename}/html"
          data['launchAtStartUp'] = File.exists? startup_filepath
          data['mainScript'] = data['launchAtStartUp'] ? startup_filepath.pathmap("%f") : ''
          data['timeStamp'] = Time.now.to_f
          data['addToMenu'] = menu_scripts.to_a.collect {|i| MenuItem.new(i).to_hash}
          data.save_plist t.name
        end
        CLOBBER.include("#{bundle_filename}/info.plist")

        task plist: %W[#{bundle_filename} #{bundle_filename}/info.plist]

        desc "Compiles an extension from #{src_filepath}"
        task build: [:clean, :clobber, :source, :plist]

        desc "Compiles and installs an extension from #{src_filepath}"
        task :install => :build do
          sh "open #{bundle_filename}"
        end

        desc "Blindly uninstalls an installed #{extension_name} extension"
        task :uninstall do
          sh "rm -rf ~/Library/Application\\ Support/RoboFont/plugins/#{bundle_filename}"
        end
      end

    end
  end
end
