#!/usr/bin/env python3
"""Generate a directly openable Xcode .xcodeproj without requiring XcodeGen."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parents[1]
out = root / 'NOVA-SMS-Shield-AI.xcodeproj' / 'project.pbxproj'
ids = {}
def uid(name):
    if name not in ids: ids[name]=hashlib.sha256(name.encode()).hexdigest()[:24].upper()
    return ids[name]

def obj(tag,isa,**fields):
    parts=[f'\t\t{uid(tag)} /* {tag} */ = {{',f'\t\t\tisa = {isa};']
    for k,v in fields.items(): parts.append(f'\t\t\t{k} = {v};')
    return '\n'.join(parts)+'\n\t\t};'

def ref(name): return f'{uid(name)} /* {name} */'
def array(names): return '(\n' + ''.join(f'\t\t\t\t{ref(x)},\n' for x in names) + '\t\t\t)'
def quoted(text): return '"'+text.replace('"','\\"')+'"'
def settings(data):
    s='{\n'
    for k,v in data.items():
        s+=f'\t\t\t\t{k} = {v};\n'
    return s+'\t\t\t}'

objects=[]
objects.append(obj('PROJECT','PBXProject',
    attributes='{ LastUpgradeCheck = 1600; TargetAttributes = { '+uid('TARGET_APP')+' = { CreatedOnToolsVersion = 16.0; }; '+uid('TARGET_EXT')+' = { CreatedOnToolsVersion = 16.0; }; }; }',
    buildConfigurationList=ref('PROJ_CONFIG_LIST'),compatibilityVersion=quoted('Xcode 14.0'),
    developmentRegion='tr',hasScannedForEncodings='0',knownRegions='(tr, en, Base,)',
    mainGroup=ref('ROOT_GROUP'),productRefGroup=ref('PRODUCT_GROUP'),projectDirPath=quoted(''),projectRoot=quoted(''),
    targets=array(['TARGET_APP','TARGET_EXT'])))

objects.append(obj('ROOT_GROUP','PBXGroup',children=array(['GROUP_APP','GROUP_EXT','GROUP_SHARED','GROUP_TOOLS','PRODUCT_GROUP']),sourceTree=quoted('<group>')))
objects.append(obj('GROUP_APP','PBXGroup',children=array(['FILE_APP','FILE_CONTENT','FILE_APP_PLIST']),path=quoted('NOVA-SMS-Shield-AI'),sourceTree=quoted('<group>')))
objects.append(obj('GROUP_EXT','PBXGroup',children=array(['FILE_EXT','FILE_EXT_PLIST']),path='MessageFilter',sourceTree=quoted('<group>')))
objects.append(obj('GROUP_SHARED','PBXGroup',children=array(['FILE_ANALYZER','FILE_MODEL']),path='Shared',sourceTree=quoted('<group>')))
objects.append(obj('GROUP_TOOLS','PBXGroup',children=array(['FILE_TRAIN']),path='Tools',sourceTree=quoted('<group>')))
objects.append(obj('PRODUCT_GROUP','PBXGroup',children=array(['PRODUCT_APP','PRODUCT_EXT']),name='Products',sourceTree=quoted('<group>')))

for name,path,ftype in [
 ('FILE_APP','NOVASMSShieldAIApp.swift','sourcecode.swift'),
 ('FILE_CONTENT','ContentView.swift','sourcecode.swift'),
 ('FILE_APP_PLIST','Info.plist','text.plist.xml'),
 ('FILE_EXT','MessageFilterExtension.swift','sourcecode.swift'),
 ('FILE_EXT_PLIST','Info.plist','text.plist.xml'),
 ('FILE_ANALYZER','SMSAnalyzer.swift','sourcecode.swift'),
 ('FILE_MODEL','sms_model.json','text.json'),
 ('FILE_TRAIN','train_model.py','text.script.python'),
]:
    objects.append(obj(name,'PBXFileReference',lastKnownFileType=ftype,path=quoted(path),sourceTree=quoted('<group>')))
objects.append(obj('PRODUCT_APP','PBXFileReference',explicitFileType='wrapper.application',includeInIndex='0',path='NOVASMSShieldAI.app',sourceTree='BUILT_PRODUCTS_DIR'))
objects.append(obj('PRODUCT_EXT','PBXFileReference',explicitFileType='wrapper.app-extension',includeInIndex='0',path='MessageFilter.appex',sourceTree='BUILT_PRODUCTS_DIR'))

for name,fileref,extra in [
 ('BUILD_APP','FILE_APP',None),('BUILD_CONTENT','FILE_CONTENT',None),
 ('BUILD_SHARED_APP','FILE_ANALYZER',None),('BUILD_MODEL_APP','FILE_MODEL',None),
 ('BUILD_EXT','FILE_EXT',None),('BUILD_SHARED_EXT','FILE_ANALYZER',None),
 ('BUILD_MODEL_EXT','FILE_MODEL',None),
 ('BUILD_EMBED_EXT','PRODUCT_EXT','{ATTRIBUTES = (CodeSignOnCopy, RemoveHeadersOnCopy, ); }'),
]:
    fields={'fileRef':ref(fileref)}
    if extra: fields['settings']=extra
    objects.append(obj(name,'PBXBuildFile',**fields))

objects.append(obj('APP_SOURCES','PBXSourcesBuildPhase',buildActionMask='2147483647',files=array(['BUILD_APP','BUILD_CONTENT','BUILD_SHARED_APP']),runOnlyForDeploymentPostprocessing='0'))
objects.append(obj('EXT_SOURCES','PBXSourcesBuildPhase',buildActionMask='2147483647',files=array(['BUILD_EXT','BUILD_SHARED_EXT']),runOnlyForDeploymentPostprocessing='0'))
objects.append(obj('APP_RESOURCES','PBXResourcesBuildPhase',buildActionMask='2147483647',files=array(['BUILD_MODEL_APP']),runOnlyForDeploymentPostprocessing='0'))
objects.append(obj('EXT_RESOURCES','PBXResourcesBuildPhase',buildActionMask='2147483647',files=array(['BUILD_MODEL_EXT']),runOnlyForDeploymentPostprocessing='0'))
objects.append(obj('APP_FRAMEWORKS','PBXFrameworksBuildPhase',buildActionMask='2147483647',files='()',runOnlyForDeploymentPostprocessing='0'))
objects.append(obj('EXT_FRAMEWORKS','PBXFrameworksBuildPhase',buildActionMask='2147483647',files='()',runOnlyForDeploymentPostprocessing='0'))
objects.append(obj('APP_EMBED','PBXCopyFilesBuildPhase',buildActionMask='2147483647',dstPath=quoted(''),dstSubfolderSpec='13',files=array(['BUILD_EMBED_EXT']),name=quoted('Embed App Extensions'),runOnlyForDeploymentPostprocessing='0'))

objects.append(obj('EXT_PROXY','PBXContainerItemProxy',containerPortal=ref('PROJECT'),proxyType='1',remoteGlobalIDString=uid('TARGET_EXT'),remoteInfo='MessageFilter'))
objects.append(obj('EXT_DEPENDENCY','PBXTargetDependency',target=ref('TARGET_EXT'),targetProxy=ref('EXT_PROXY')))
objects.append(obj('TARGET_APP','PBXNativeTarget',buildConfigurationList=ref('APP_CONFIG_LIST'),buildPhases=array(['APP_SOURCES','APP_FRAMEWORKS','APP_RESOURCES','APP_EMBED']),buildRules='()',dependencies=array(['EXT_DEPENDENCY']),name='NOVASMSShieldAI',productName='NOVASMSShieldAI',productReference=ref('PRODUCT_APP'),productType=quoted('com.apple.product-type.application')))
objects.append(obj('TARGET_EXT','PBXNativeTarget',buildConfigurationList=ref('EXT_CONFIG_LIST'),buildPhases=array(['EXT_SOURCES','EXT_FRAMEWORKS','EXT_RESOURCES']),buildRules='()',dependencies='()',name='MessageFilter',productName='MessageFilter',productReference=ref('PRODUCT_EXT'),productType=quoted('com.apple.product-type.app-extension')))

projectSettings={
 'ALWAYS_SEARCH_USER_PATHS':'NO','CLANG_ENABLE_MODULES':'YES','CLANG_ENABLE_OBJC_ARC':'YES',
 'COPY_PHASE_STRIP':'NO','GCC_C_LANGUAGE_STANDARD':'gnu17','IPHONEOS_DEPLOYMENT_TARGET':'16.0',
 'SDKROOT':'iphoneos','SWIFT_VERSION':'5.0',
}
for mode in ['Debug','Release']:
    ps=dict(projectSettings)
    ps['SWIFT_OPTIMIZATION_LEVEL']=quoted('-Onone') if mode=='Debug' else quoted('-O')
    ps['DEBUG_INFORMATION_FORMAT']='dwarf' if mode=='Debug' else quoted('dwarf-with-dsym')
    ps['ENABLE_TESTABILITY']='YES' if mode=='Debug' else 'NO'
    ps['GCC_OPTIMIZATION_LEVEL']='0' if mode=='Debug' else 's'
    if mode=='Debug': ps['SWIFT_ACTIVE_COMPILATION_CONDITIONS']='DEBUG'
    objects.append(obj('PROJ_'+mode,'XCBuildConfiguration',buildSettings=settings(ps),name=mode))
    app={
      'ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS':'YES',
      'CODE_SIGN_STYLE':'Automatic','CURRENT_PROJECT_VERSION':'1',
      'GENERATE_INFOPLIST_FILE':'NO','INFOPLIST_FILE':quoted('NOVA-SMS-Shield-AI/Info.plist'),
      'IPHONEOS_DEPLOYMENT_TARGET':'16.0','LD_RUNPATH_SEARCH_PATHS':quoted('$(inherited) @executable_path/Frameworks'),
      'MARKETING_VERSION':'0.1.0','PRODUCT_BUNDLE_IDENTIFIER':'com.example.NOVASMSShieldAI',
      'PRODUCT_NAME':quoted('$(TARGET_NAME)'),
      'SUPPORTED_PLATFORMS':quoted('iphoneos iphonesimulator'),
      'SUPPORTS_MACCATALYST':'NO', 'SWIFT_VERSION':'5.0','TARGETED_DEVICE_FAMILY':'1',
    }
    ext={
      'APPLICATION_EXTENSION_API_ONLY':'YES','CODE_SIGN_STYLE':'Automatic',
      'CURRENT_PROJECT_VERSION':'1','GENERATE_INFOPLIST_FILE':'NO',
      'INFOPLIST_FILE':'MessageFilter/Info.plist',
      'IPHONEOS_DEPLOYMENT_TARGET':'16.0',
      'LD_RUNPATH_SEARCH_PATHS':quoted('$(inherited) @executable_path/Frameworks @executable_path/../../Frameworks'),
      'MARKETING_VERSION':'0.1.0','PRODUCT_BUNDLE_IDENTIFIER':'com.example.NOVASMSShieldAI.MessageFilter',
      'PRODUCT_NAME':quoted('$(TARGET_NAME)'),
      'SKIP_INSTALL':'YES','SUPPORTED_PLATFORMS':quoted('iphoneos iphonesimulator'),
      'SUPPORTS_MACCATALYST':'NO','SWIFT_VERSION':'5.0','TARGETED_DEVICE_FAMILY':'1',
    }
    objects.append(obj('APP_'+mode,'XCBuildConfiguration',buildSettings=settings(app),name=mode))
    objects.append(obj('EXT_'+mode,'XCBuildConfiguration',buildSettings=settings(ext),name=mode))

for name,configs in [('PROJ_CONFIG_LIST',['PROJ_Debug','PROJ_Release']),('APP_CONFIG_LIST',['APP_Debug','APP_Release']),('EXT_CONFIG_LIST',['EXT_Debug','EXT_Release'])]:
    objects.append(obj(name,'XCConfigurationList',buildConfigurations=array(configs),defaultConfigurationIsVisible='0',defaultConfigurationName='Release'))

contents='// !$*UTF8*$!\n{\n\tarchiveVersion = 1;\n\tclasses = {};\n\tobjectVersion = 56;\n\tobjects = {\n'
contents+='\n'.join(objects)
contents+='\n\t};\n\trootObject = '+ref('PROJECT')+';\n}\n'
out.write_text(contents,encoding='utf-8')
print('Wrote',out,'objects',len(objects))
