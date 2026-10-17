// Reference-only generator. Download the pinned upstream repository to ignored work/.
// Usage: node testing/D2/generate-semver-fixtures.cjs work/semver-reference
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const ref = path.resolve(process.argv[2] || 'work/semver-reference');
const commit = '281055e7716ef0415a8826972471331989ede58c';
if (cp.execFileSync('git', ['-C', ref, 'rev-parse', 'HEAD'], {encoding:'utf8'}).trim() !== commit) throw Error('Reference commit differs');
const semver = require(ref);
if (require(path.join(ref,'package.json')).version !== '7.7.2') throw Error('Reference version differs');
const strict = v => typeof v === 'string' && /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/.test(v) && !!semver.valid(v);
const vectors = new Map();
const add=(version,range,expected)=>vectors.set(JSON.stringify([version,range]),{version,range,expected});
const ranges = new Set(['','*','x','X','1.x','0.x','0.0.x','1.2.X','v1.2.3','=1.2.3','~>1.2','>=1.2.3 <2.0.0 || ^3.0.0','* || ^1.2.3-alpha','>=1.2.3-alpha <1.2.3','<0.0.0-0','>x','<=x']);
const versions = new Set(['0.0.0','0.0.0-0','0.0.1','0.1.0','0.2.0','1.0.0','1.2.3','1.2.3-alpha','1.2.3-alpha.1','1.2.3-alpha.2','1.2.3-alpha.10','1.2.3-beta','1.2.3+build.01','1.2.4-0','1.3.0','2.0.0-0','2.0.0','3.0.0','3.4.5','4.0.0']);
let upstream=0,excluded=0;
for (const [name,expected] of [['range-include','MATCH'],['range-exclude','NO_MATCH']]) {
 for (const [range,version,opts] of require(path.join(ref,'test/fixtures',name+'.js'))) {
  if (!strict(version) || opts===true || opts?.loose || opts?.includePrerelease || !semver.validRange(range)) {excluded++;continue;}
  const actual=semver.satisfies(version,range)?'MATCH':'NO_MATCH';
  if(actual!==expected)throw Error('Unexpected upstream fixture result');
  add(version,range,expected);ranges.add(range);versions.add(version);upstream++;
 }
}
for (const [range,,opts] of require(path.join(ref,'test/fixtures/range-parse.js'))) {
 if (typeof range==='string' && opts!==true && !opts?.loose && !opts?.includePrerelease && semver.validRange(range)) ranges.add(range);
}
for (const [version] of require(path.join(ref,'test/fixtures/valid-versions.js'))) if(strict(version)) versions.add(version);
for (const [a,b,opts] of require(path.join(ref,'test/fixtures/comparisons.js'))) {
 if(opts===true || opts?.loose)continue;
 if(strict(a))versions.add(a);if(strict(b))versions.add(b);
}
for (const range of ['1.x.3','x.2.3','1.x.x-pre','1.x.3-beta','* || >=1.2.3-alpha','>=1.0.0 ||','||','>X','<=1.x','<1.2.x','~ 1.2','^ 0.0','1.2.3-0 || <0.0.0-0','>=0.0.0 || >=1.2.3-alpha','v1.2 - v2.3','1.2.3+001 - 2.0.0+002','vv1.x','==1.x','^vv1.2.3','~==1.2.3','>=\u00a01.2.3','\ufeff^1.2.3','>=\u20031.2.3 <2']) {
 if(!semver.validRange(range)) throw Error('Invalid added reference range');ranges.add(range);
}
// Reproducible boundary lattice: each grammar family against stable/prerelease/build candidates.
for(const base of ['0','0.0','0.0.1','0.1','0.1.2','1','1.2','1.2.3','1.2.3-alpha','1.2.3-alpha.1','2.0.0','3.4.5']) {
 for(const op of ['','=', '<','<=','>','>=','~','~>','^']) ranges.add(op+base);
}
for(const range of ranges) for(const version of versions) {
 add(version,range,semver.satisfies(version,range)?'MATCH':'NO_MATCH');
}
// Invalid range syntax is a separate diagnostic; never silently ignore an invalid OR arm.
for(const range of ['banana','>=1.0.0 || garbage','1.2.3, <2','1.2.3.4','^^1.2.3','>=','!=1.2.3','1.2.3 -','01.2.3','1.2.3-01','1.2.3+','1.2.3 || <','1 | 2','1.2.3\ninvalid','==1.2.3','vv1.2.3','>=v=1.2.3']) {
 if(semver.validRange(range)!==null)throw Error('Expected invalid range');
 add('1.2.3',range,'INVALID_RANGE');
}
for(const version of ['01.2.3','1.02.3','1.2.03','1.2','v1.2.3','=1.2.3','1.2.3-01','1.2.3-','1.2.3+','1.2.3-a..b','1.2.3-a_b','1.2.3\n','1.2.3+é']) add(version,'*','INVALID_VERSION');
const rows=[...vectors.values()];
const out=path.join(__dirname,'src/test/resources/semver');
for(const name of fs.readdirSync(out))if(/^conformance.*\.json$/.test(name))fs.unlinkSync(path.join(out,name));
for(let i=0;i<rows.length;i+=5000)fs.writeFileSync(path.join(out,`conformance-${String(i/5000+1).padStart(2,'0')}.json`),JSON.stringify(rows.slice(i,i+5000))+'\n');
fs.writeFileSync(path.join(out,'metadata.json'),JSON.stringify({reference:'npm/node-semver',version:'7.7.2',commit,options:{loose:false,includePrerelease:false},stored_versions:'Strict SemVer 2.0.0, no v/= prefix or surrounding whitespace',upstream_rows:upstream,excluded_upstream_rows:excluded,excluded_options:'loose/includePrerelease, noncanonical stored versions, invalid ranges',ranges:ranges.size,versions:versions.size,vectors:rows.length,license:'ISC; see THIRD-PARTY-NOTICES.md'},null,2)+'\n');
console.log(JSON.stringify({vectors:rows.length,ranges:ranges.size,versions:versions.size,upstream,excluded}));
